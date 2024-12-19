from fastapi import FastAPI
from app.users.router import router as router_users
from app.trainers.router import router as router_trainers
from app.athletes.router import router as router_athletes
from app.reports.router import router as router_reports


app = FastAPI()

@app.get("/")
def home_page():
    return {"message": "Привет, Абоба!"}

app.include_router(router_users)
app.include_router(router_trainers)
app.include_router(router_athletes)
app.include_router(router_reports)

