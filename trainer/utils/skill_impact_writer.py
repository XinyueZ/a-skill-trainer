from pydantic import BaseModel, ConfigDict


class SkillImpactWriter(BaseModel):
    model_config = ConfigDict(extra="forbid")
