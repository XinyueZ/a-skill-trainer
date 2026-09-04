import os
from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from layers.raw_layer import RawLayer
from loguru import logger
from pydantic import BaseModel, ConfigDict
from utils.run_agent import run_agent
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

    async def __call__(self, **kwargs):
        session_id = kwargs["session_id"]
        system_prompt = kwargs.get("system_prompt")
        logger.debug(f"system prompt:\n\n{system_prompt[:150]}...\n\n")

        query = kwargs["query"]
        task = kwargs["task"]
        output_dir = kwargs["output_dir"]
        skills = kwargs.get("skills")
        tools = kwargs.get("tools", [])
        stream_mode = kwargs.get("stream_mode") == True

        self._agent = create_deep_agent(
            model=self._model,
            skills=skills,
            tools=tools,
            system_prompt=system_prompt,
        )
        logger.info(
            f"Start inferencing for task {task}, query: {query}, output_dir: {output_dir}"
        )

        messages = [{"role": "user", "content": query}]
        response = await run_agent(self._agent, messages, stream_mode)

        list_messages = response["messages"]
        traces_path = self._raw_layer.append_traces(
            session_id, task.id, list_messages, output_dir
        )
        logger.success(f"Inference done, addd traces to raw layer at {traces_path}")


async def main(args):

    task = Task(id=args.task_id, name=args.task_name)
    session_id = create_session_id()

    skill_dir_str = args.skill_dir
    skill_dir_list = skill_dir_str.split() if skill_dir_str else None

    inference_agent = InferenceAgent()
    await inference_agent(
        session_id=session_id,
        query=args.query,
        task=task,
        output_dir=args.output_dir,
        system_prompt=args.system_prompt,
        skills=skill_dir_list,
        stream_mode=args.stream_mode,
    )


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
        "--skill_dir",
        type=str,
        required=False,
        help="Skill directory",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        default="../output",
        help="Output directory",
    )
    parser.add_argument(
        "--stream_mode",
        action="store_true",
        help="Set for stream mode",
    )

    args = parser.parse_args()

    # python inference_agent.py --task_id 1234455 --task_name development-task --query "What is the capital of China?"  --output_dir ../output --stream_mode
    # python inference_agent.py --task_id 1234455 --task_name development-task --query "What is the capital of China?" --system_prompt "Answer user question and finish task." --skill_dir ../workspace/skills --output_dir ../output --stream_mode
    # python inference_agent.py --task_id 1234455 --task_name development-task --query "What is the capital of China?" --system_prompt "Answer user question and finish task. Always use finish tool for complete signal" --skill_dir ../workspace/skills --output_dir ../output --stream_mode
    # python inference_agent.py --task_id 1234455 --task_name development-task --query "Current weather in Hamburg Germany please" --system_prompt "Answer user question and finish task. Your answers must be based on true and reality, avoid answering that you do not know" --skill_dir ../workspace/skills --output_dir ../output --stream_mode
    import asyncio

    asyncio.run(main(args))
