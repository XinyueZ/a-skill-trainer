from pydantic import BaseModel, ConfigDict


class WikiLayer(BaseModel):
    model_config = ConfigDict(extra="forbid")
