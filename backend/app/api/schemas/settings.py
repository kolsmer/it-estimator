from pydantic import BaseModel


class RateUpdateInput(BaseModel):
    role: str
    seniority: str
    rate: float
