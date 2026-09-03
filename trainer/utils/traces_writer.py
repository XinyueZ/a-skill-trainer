from pydantic import BaseModel, ConfigDict


class TracesWriter(BaseModel):
    model_config = ConfigDict(extra="forbid")
