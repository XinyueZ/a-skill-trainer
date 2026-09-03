from pydantic import BaseModel, ConfigDict


class PatternsWriter(BaseModel):
    model_config = ConfigDict(extra="forbid")
