from pydantic import BaseModel, ConfigDict


class LogWriter(BaseModel):
    model_config = ConfigDict(extra="forbid")
