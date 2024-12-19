from pydantic import BaseModel


class SCompetitions(BaseModel):
    title: str
    data: str