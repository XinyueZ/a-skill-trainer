from pydantic import BaseModel, ConfigDict


class SkillImpactReader(BaseModel):
    model_config = ConfigDict(extra="forbid")
