import os

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from layers.raw_layer import RawLayer
from loguru import logger
from pydantic import BaseModel, ConfigDict
from utils.session_creator import create_session_id
from langchain.tools import tool

load_dotenv()


@tool
def finish(some_message: str) -> str:
    """
    Finish, when the user has done the assigened task, receive some message from caller and return finish message.

    Args:
        some_message (str): A message
    Returns:
        str: A finish message
    """

    return "this is finish message"


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

        self._agent = create_deep_agent(model=self._model, tools=[finish])
        self._raw_layer = RawLayer()

    def __call__(self, **kwargs):
        query = kwargs["query"]
        task = kwargs["task"]
        root_path = kwargs["root_path"]

        logger.info(
            f"Start inference for task {task}, query: {query}, root_path: {root_path}"
        )
        response = self._agent.invoke(
            {
                "messages": [
                    {
                        "role": "system",
                        "content": "Answer user question and call tool `finish` with some message when done",
                    },
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
    agent(query="What is the capital of China?", task=task.id, root_path=root_path)
