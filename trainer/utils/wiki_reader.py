from pydantic import BaseModel, ConfigDict


class WikiReader(BaseModel):
    model_config = ConfigDict(extra="forbid")
