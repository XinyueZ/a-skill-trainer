import os

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from layers.raw_layer import RawLayer
from loguru import logger
from pydantic import BaseModel, ConfigDict
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

    def __call__(self, **kwargs):
        system_prompt = (
            [kwargs.get("system_prompt")] if kwargs.get("system_prompt") else list()
        )
        query = kwargs["query"]
        task = kwargs["task"]
        root_path = kwargs["root_path"]
        tools = kwargs.get("tools", list())

        self._agent = create_deep_agent(model=self._model, tools=tools)
        logger.info(
            f"Start inference for task {task}, query: {query}, root_path: {root_path}"
        )
        response = self._agent.invoke(
            {
                "messages": system_prompt
                + [
                    {"role": "user", "content": query},
                ]
            }
        )

        list_messages = response["messages"]
        traces_path = self._raw_layer.append_traces(task, list_messages, root_path)
        logger.success(f"Inference done, addd traces to raw layer at {traces_path}")


if __name__ == "__main__":
    task = Task(id="12345", name="development-task")

    session_id = create_session_id()
    root_path = f"../output/{session_id}"

    agent = InferenceAgent()
    agent(
        query="What is the capital of China?",
        task=task.id,
        root_path=root_path,
        system_prompt="Answer user question and finish task.",
    )
