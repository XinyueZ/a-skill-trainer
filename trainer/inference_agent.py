import os
import tempfile
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import ToolMessage
from layers.raw_layer import RawLayer
from loguru import logger
from pydantic import BaseModel, ConfigDict
from utils.awrap_tool_call import AwrapToolCall
from utils.get_current_datetime import get_current_local_datetime
from utils.run_agent import run_deepagents
from utils.run_python import create_run_python
from utils.session_creator import create_session_id

load_dotenv()


class Task(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    name: str


class InferenceAgent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    _raw_layer: RawLayer

    def __init__(self):
        self._model = init_chat_model(
            model=os.environ["INFERENCE_MODEL"],
            model_provider="google_genai",
            temperature=float(os.environ["TEMPERATURE"]),
            vertexai=os.environ["GOOGLE_GENAI_USE_VERTEXAI"].lower() == "true",
            enterprise=os.environ["GOOGLE_GENAI_USE_ENTERPRISE"].lower() == "true",
            project=os.environ["GOOGLE_CLOUD_PROJECT"],
            location=os.environ["INFERENCE_MODEL_LOCATION"],
            thinking_config={
                "thinking_level": os.environ["THINKING_LEVEL"],
                "include_thoughts": os.environ["INCLUDE_THOUGHTS"].lower() == "true",
            },
        )

        self._raw_layer = RawLayer()

    def _create_block_forbidden_files(self, root_dir):
        def _block_forbidden_files(request, handler):
            tool_name = request.tool_call.get("name", "")
            args = request.tool_call.get("args", {})

            raw_path = args.get("file_path") or args.get("path") or ""
            if (
                not str(Path(raw_path).resolve()).startswith(
                    str(Path(root_dir).resolve())
                )
                and tool_name != "run_python"
            ):
                logger.warning(
                    f"Block forbidden action on non-wiki directory: tool={tool_name}, path='{raw_path}', **ONLY ALLOWED** in '{root_dir}'"
                )
                return ToolMessage(
                    content=f"Access to the non-wiki directory is strictly forbidden. **ONLY ALLOWED** in '{root_dir}'",
                    name=tool_name,
                    tool_call_id=request.tool_call.get("id", "avoid"),
                )

            return handler(request)

        return _block_forbidden_files

    async def __call__(self, **kwargs):
        session_id = kwargs["session_id"]
        assert session_id, "session_id must be specified"

        system_prompt = kwargs.get("system_prompt")
        logger.debug(f"system prompt:\n\n{system_prompt[:150]}...\n\n")

        query = kwargs["query"]
        assert query, "query must be specified"

        task = kwargs["task"]
        assert task, "task must be specified"

        output_dir = kwargs["output_dir"]
        assert output_dir, "output_dir must be specified"
        output_abs_path = Path(output_dir)

        skills_dir_list = kwargs.get("skills_dir_list")
        if len(skills_dir_list) == 0:
            skills_abs_dir_path_list = None
        else:
            skills_abs_dir_path_list = [
                os.path.abspath(skill_dir) for skill_dir in skills_dir_list
            ]

        sandbox_output = os.path.abspath("./sandbox_output")
        sandbox_output = Path(sandbox_output).resolve() / str(session_id)
        run_python_tool = create_run_python(sandbox_output)
        tools = [run_python_tool] + kwargs.get("tools", list())
        # tools = kwargs.get("tools")
        system_prompt = f"""{system_prompt}
---
Additionally, if you wish to write code to accomplish specific tasks, 
you can duplicate this program file and 
utilize the `run_python` tool to execute the code you write in a sandbox environment.
---
Current session ID: {session_id}
---
Current datetime {get_current_local_datetime()}
"""

        stream_mode = kwargs.get("stream_mode") == True

        fs_backend = FilesystemBackend(root_dir=sandbox_output, virtual_mode=False)
        backend = CompositeBackend(
            default=fs_backend, routes={}, artifacts_root=tempfile.gettempdir()
        )
        self._agent = create_deep_agent(
            model=self._model,
            skills=skills_abs_dir_path_list,
            tools=tools,
            backend=backend,
            system_prompt=system_prompt,
            middleware=[
                AwrapToolCall(self._create_block_forbidden_files(sandbox_output))
            ],
        )
        logger.info(
            f"Start inferencing for task {task}, query: {query}, output_abs_path: {output_abs_path}\n\n"
        )

        messages = [{"role": "user", "content": query}]
        response = await run_deepagents(self._agent, messages, stream_mode)

        list_messages = response["messages"]
        traces_path = self._raw_layer.append_traces(
            session_id, task.id, list_messages, output_abs_path
        )
        logger.success(f"Inference done, addd traces to raw layer at {traces_path}")


async def main(args):

    task = Task(id=args.task_id, name=args.task_name)
    session_id = create_session_id()

    skills_dir_str = args.skills_dir or ""
    skills_dir_list = skills_dir_str.split(";")

    inference_agent = InferenceAgent()
    await inference_agent(
        session_id=session_id,
        query=args.query,
        task=task,
        output_dir=args.output_dir,
        system_prompt=args.system_prompt,
        skills_dir_list=skills_dir_list,
        stream_mode=args.stream_mode,
    )

    return session_id


if __name__ == "__main__":
    # read cli args
    from argparse import ArgumentParser

    parser = ArgumentParser(allow_abbrev=False)
    parser.add_argument(
        "--task_id",
        type=str,
        required=True,
        help="Task id",
    )
    parser.add_argument(
        "--task_name",
        type=str,
        required=True,
        help="Task name",
    )
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Query that the user questions.",
    )
    parser.add_argument(
        "--system_prompt",
        type=str,
        required=False,
        help="System prompt",
    )
    parser.add_argument(
        "--skills_dir",
        type=str,
        required=False,
        help="Skill directory",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        default="./output",
        help="Output directory",
    )
    parser.add_argument(
        "--stream_mode",
        action="store_true",
        help="Set for stream mode",
    )

    args = parser.parse_args()

    # python trainer/inference_agent.py --task_id 1234455 --task_name development-task --query "Current weather in Hamburg Germany please" --system_prompt "Answer user question and finish task. Your answers must be based on true and reality, avoid answering that you do not know" --skills_dir ./workspace/skills --output_dir ./output --stream_mode
    import asyncio

    session_id = asyncio.run(main(args))

    print(session_id)
