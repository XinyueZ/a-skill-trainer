from pydantic import BaseModel, ConfigDict


class ProposalApplier(BaseModel):
    model_config = ConfigDict(extra="forbid")
