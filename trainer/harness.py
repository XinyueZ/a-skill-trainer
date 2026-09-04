from pydantic import BaseModel, ConfigDict
from trainer.layers.raw_layer import RawLayer
from trainer.layers.skills_layer import SkillsLayer
from trainer.layers.wiki_layer import WikiLayer


class Harness(BaseModel):
    model_config = ConfigDict(extra="forbid")

    _raw_layer: RawLayer
    _skills_layer: SkillsLayer
    _wiki_layer: WikiLayer

    def reject():
        pass

    def accept():
        pass
