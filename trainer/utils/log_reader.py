from pydantic import BaseModel, ConfigDict


class LogReader(BaseModel):
    model_config = ConfigDict(extra="forbid")
