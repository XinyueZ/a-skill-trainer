from pydantic import BaseModel, ConfigDict


class SkillsLayer(BaseModel):
    model_config = ConfigDict(extra="forbid")
