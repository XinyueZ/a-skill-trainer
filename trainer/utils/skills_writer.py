from pydantic import BaseModel, ConfigDict


class SkillsWriter(BaseModel):
    model_config = ConfigDict(extra="forbid")
