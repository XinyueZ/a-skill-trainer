from pydantic import BaseModel, ConfigDict


class WikiMaintaincer(BaseModel):
    model_config = ConfigDict(extra="forbid")
