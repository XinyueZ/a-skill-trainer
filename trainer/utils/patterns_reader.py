from pydantic import BaseModel, ConfigDict


class PatternsReader(BaseModel):
    model_config = ConfigDict(extra="forbid")
