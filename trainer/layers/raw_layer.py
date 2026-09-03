from pydantic import BaseModel, ConfigDict


class RawLayer(BaseModel):
    model_config = ConfigDict(extra="forbid")
