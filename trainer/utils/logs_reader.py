from pydantic import BaseModel, ConfigDict


class LogsReader(BaseModel):
    model_config = ConfigDict(extra="forbid")
