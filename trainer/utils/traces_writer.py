import json
import os
from pathlib import Path

from google.antigravity.types import Step
from langchain_core.load import dumps
from loguru import logger
from pydantic import BaseModel, ConfigDict


class TracesPath(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: Path
    abs_path: Path


class _Cleaner(BaseModel):
    model_config = ConfigDict(extra="forbid")

    def _remove_key(self, a_dict, key):
        if key in a_dict:
            a_dict.pop(key)
        return a_dict

    def _remove_keys(self, a_dict, *keys):
        for key in keys:
            if key in a_dict:
                a_dict.pop(key)
        return a_dict


class _LangChainMessageListCleaner(_Cleaner):
    def __call__(self, **kwargs):
        cleaned_kwargs = {
            "source": kwargs["type"],
        }
        if kwargs["content"]:
            cleaned_content = (
                list(map(lambda x: self._remove_key(x, "extras"), kwargs["content"]))
                if isinstance(kwargs["content"], list)
                else self._remove_key(kwargs["content"], "extras")
            )
            cleaned_kwargs["content"] = cleaned_content

        if "tool_calls" in kwargs and kwargs["tool_calls"]:
            cleaned_kwargs["tool_calls"] = list(
                map(lambda x_dict: self._remove_key(x_dict, "id"), kwargs["tool_calls"])
            )

        if kwargs["type"] == "tool":
            cleaned_kwargs["name"] = kwargs["name"]
            cleaned_kwargs["status"] = kwargs["status"]

        return cleaned_kwargs


class _AntigravityStepHistoryCleaner(_Cleaner):

    def __call__(self, **kwargs):
        cleaned_kwargs = {"soruce": kwargs["source"]}
        if kwargs["content"]:
            cleaned_kwargs["content"] = kwargs["content"]
        if kwargs["thinking"]:
            cleaned_kwargs["thinking"] = kwargs["thinking"]
        if kwargs["tool_calls"]:
            cleaned_kwargs["tool_calls"] = kwargs["tool_calls"]
            cleaned_kwargs["tool_calls"] = list(
                map(
                    lambda x_dict: self._remove_keys(
                        x_dict, "id", "step_id", "canonical_path", "server_name"
                    ),
                    kwargs["tool_calls"],
                )
            )
        return cleaned_kwargs


class TracesWriter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    def append(self, task_id, list_messages, root_path) -> TracesPath:
        dir_path = os.path.join(str(root_path), task_id)
        file_path = os.path.join(dir_path, "traces.json")
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        with open(file_path, "a", encoding="utf-8") as f:
            json_str = dumps(list_messages, pretty=True)

            # if Antigravity history steps
            if isinstance(list_messages, list) and isinstance(list_messages[0], Step):
                predumpy_list = list(
                    map(
                        lambda step: _AntigravityStepHistoryCleaner()(
                            **step.model_dump(mode="json")
                        ),
                        list_messages,
                    )
                )
            else:
                invers_json = json.loads(json_str)
                predumpy_list = list(
                    map(
                        lambda x: _LangChainMessageListCleaner()(**x["kwargs"]),
                        invers_json,
                    )
                )

            json_str = json.dumps(predumpy_list, indent=2, ensure_ascii=False)
            f.write(json_str)
            abs_path = Path(file_path).resolve()
            traces_path = TracesPath(path=Path(file_path), abs_path=abs_path)
            logger.success(f"Write traces to {traces_path}")

            return traces_path
