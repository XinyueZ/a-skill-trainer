from pydantic import BaseModel, ConfigDict


class LogsWriter(BaseModel):
    model_config = ConfigDict(extra="forbid")
