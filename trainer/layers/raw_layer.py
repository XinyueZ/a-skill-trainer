from pydantic import BaseModel, ConfigDict
from utils.traces_reader import TracesReader
from utils.traces_writer import TracesPath, TracesWriter
from pathlib import Path
import os


class RawLayer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    _traces_reader: TracesReader
    _traces_writer: TracesWriter

    def __init__(self):
        self._traces_writer = TracesWriter()
        self._traces_reader = TracesReader()

    def append_traces(
        self, session_id, task_id, list_messages, output_dir
    ) -> TracesPath:
        root_path = Path(os.path.join(output_dir, session_id))
        return self._traces_writer.append(task_id, list_messages, root_path)

    def read_traces(self, traces_dir_path) -> dict:
        return self._traces_reader.read(traces_dir_path)
