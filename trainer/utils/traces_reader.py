from pydantic import BaseModel, ConfigDict


class TracesReader(BaseModel):
    model_config = ConfigDict(extra="forbid")
