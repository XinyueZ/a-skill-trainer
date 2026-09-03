import json
from pathlib import Path

from langchain_core.load import dumps
from loguru import logger
from pydantic import BaseModel, ConfigDict
import os


class TracesPath(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: Path
    abs_path: Path


class TracesWriter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    def _remove_key(self, a_dict, key):
        if key in a_dict:
            a_dict.pop(key)
        return a_dict

    def _clean_kwargs(self, **kwargs):
        cleaed_kwargs = {
            "type": kwargs["type"],
        }
        if kwargs["content"]:
            cleaned_content = (
                list(map(lambda x: self._remove_key(x, "extras"), kwargs["content"]))
                if isinstance(kwargs["content"], list)
                else self._remove_key(kwargs["content"], "extras")
            )
            cleaed_kwargs["content"] = cleaned_content

        if "tool_calls" in kwargs and kwargs["tool_calls"]:
            cleaed_kwargs["tool_calls"] = list(
                map(lambda x_dict: self._remove_key(x_dict, "id"), kwargs["tool_calls"])
            )

        if kwargs["type"] == "tool":
            cleaed_kwargs["name"] = kwargs["name"]
            cleaed_kwargs["status"] = kwargs["status"]

        return cleaed_kwargs

    def append(self, task_id, list_messages, root_path) -> TracesPath:
        dir_path = os.path.join(str(root_path), task_id)
        file_path = os.path.join(dir_path, "traces.json")
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        with open(file_path, "a", encoding="utf-8") as f:
            json_str = dumps(list_messages, pretty=True)
            invers_json = json.loads(json_str)
            kwargs_list = list(
                map(lambda x: self._clean_kwargs(**x["kwargs"]), invers_json)
            )
            kwargs_list_str = json.dumps(kwargs_list, indent=2, ensure_ascii=False)
            f.write(kwargs_list_str)

            abs_path = Path(file_path).resolve()

            traces_path = TracesPath(path=Path(file_path), abs_path=abs_path)
            logger.success(f"Write traces to {traces_path}")

            return traces_path
