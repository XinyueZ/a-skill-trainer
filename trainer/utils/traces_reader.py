import json
import os
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, ConfigDict


class TracesReader(BaseModel):
    model_config = ConfigDict(extra="forbid")

    def read(self, traces_dir_path) -> dict:
        file_path = os.path.join(traces_dir_path, "traces.json")
        with open(file_path, "r", encoding="utf-8") as f:
            j = json.load(f)
            logger.success(f"Read traces from {file_path}\n\n{str(j)[:100]}....\n\n")
            return j
