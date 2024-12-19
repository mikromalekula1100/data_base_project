from fastapi import APIRouter
from app.users.dependencies import get_token
from fastapi import HTTPException, status, Depends
from jose import jwt, JWTError
from app.config import get_auth_data
from app.plan.schemas import SPlanAdd
from app.plan.dao import PlanDAO
from app.trainers.dao import TrainersDAO
from app.competitions.dao import CompetitionDAO
from app.competitions.schemas import SCompetitions
from app.athletes.dao import AthletesDAO


router = APIRouter(prefix='/trainers', tags=['Trainers'])

@router.post("/add_competition/{user_id}/")
async def add_competition(user_id: int, competition_info: SCompetitions):
    athlete_info = await AthletesDAO.get_athlete_info_by_user_id(user_id)
    athlete_id = athlete_info[0]
    competition = {
        'title': competition_info.title,
        'data': competition_info.data
    }
    await CompetitionDAO.add_competition_by_athlete_id(athlete_id, **competition)

@router.post("/plan/")
async def add_plan(plan_data: SPlanAdd):
    plan_dict = plan_data.dict()
    await PlanDAO.add_plan_by_athlete_id(**plan_dict)

@router.get("/signed_athletes/")
async def get_signed_athletes(token: str = Depends(get_token)):
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')
    user_id = payload.get('sub')
    return await TrainersDAO.get_signed_athletes(int(user_id))

@router.get("/all_trainers/")
async def get_all_trainers():
    return await TrainersDAO.get_all_trainers()

@router.get("/user_info_by_trainer_id/{trainer_id}/")
async def get_user_info_by_trainer_id(trainer_id: int):
    return await TrainersDAO.get_user_info_by_trainer_id(trainer_id)

@router.get("/athlete_reports/")
async def get_athlete_reports_by_trainer_id(token: str = Depends(get_token)):
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')
    user_id = payload.get('sub')
    trainer_id = await TrainersDAO.get_trainer_id_by_user_id_trainer(int(user_id))
    return await TrainersDAO.get_all_reports_by_trainer_id(int(trainer_id))

@router.get("/signed_athletes/competitions/")
async def get_competitions_info_for_all_users(token: str = Depends(get_token)):
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')
    user_id = payload.get('sub')
    trainer_id = await TrainersDAO.get_trainer_id_by_user_id_trainer(int(user_id))
    return await TrainersDAO.get_all_competitions(trainer_id)
