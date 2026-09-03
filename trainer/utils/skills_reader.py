from pydantic import BaseModel, ConfigDict


class SkillsReader(BaseModel):
    model_config = ConfigDict(extra="forbid")
