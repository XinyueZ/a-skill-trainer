from pydantic import BaseModel, ConfigDict


class WikiWriter(BaseModel):
    model_config = ConfigDict(extra="forbid")
