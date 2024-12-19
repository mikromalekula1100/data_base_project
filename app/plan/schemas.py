from pydantic import BaseModel


class SPlanAdd(BaseModel):
    athlete_id: int
    data_plan: str

