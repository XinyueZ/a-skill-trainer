from pydantic import BaseModel, ConfigDict


class InferenceAgent(BaseModel):
    model_config = ConfigDict(extra="forbid")
