from pydantic import BaseModel, ConfigDict


class PatternWriter(BaseModel):
    model_config = ConfigDict(extra="forbid")
