from pydantic import BaseModel


class SAdditionalInfo(BaseModel):
    athleteId: int
    age: int
    weight: int
    height: int
