from pydantic import BaseModel, ConfigDict


class SkillProposer(BaseModel):
    model_config = ConfigDict(extra="forbid")
