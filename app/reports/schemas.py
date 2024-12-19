from pydantic import BaseModel


class SReports(BaseModel):
    data: str
    planId: int
