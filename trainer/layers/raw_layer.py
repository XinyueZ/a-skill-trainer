from pydantic import BaseModel, ConfigDict
from utils.traces_reader import TracesReader
from utils.traces_writer import TracesPath, TracesWriter


class RawLayer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    _traces_reader: TracesReader
    _traces_writer: TracesWriter

    def __init__(self):
        self._traces_writer = TracesWriter()

    def append_traces(self, task_id, list_messages, root_path) -> TracesPath:
        return self._traces_writer.append(task_id, list_messages, root_path)
