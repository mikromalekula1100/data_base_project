from fastapi import APIRouter
from app.users.dependencies import get_token
from fastapi import HTTPException, status, Depends
from jose import jwt, JWTError
from app.config import get_auth_data
from app.athletes.dao import AthletesDAO
from app.additionalInfo.schemas import SAdditionalInfo


router = APIRouter(prefix='/athletes', tags=['Athletes'])


@router.post("/subscribe/{trainer_id}/")
async def subscribe(trainer_id: int, token: str = Depends(get_token)):
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')
    user_id = payload.get('sub')
    await AthletesDAO.subscribe_by_id(int(user_id), int(trainer_id))

@router.get("/my_plans/")
async def get_my_plans(token: str = Depends(get_token)):
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')
    user_id = payload.get('sub')
    return await AthletesDAO.get_plans_by_user_id(int(user_id))

@router.get("/athlete/")
async def get_my_athlete_info(token: str = Depends(get_token)):
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')
    user_id = payload.get('sub')
    athlete_data = await AthletesDAO.get_athlete_info_by_user_id(int(user_id))
    athlete = {
        'id': athlete_data[0],
        'userId': athlete_data[1],
        'trainerId': athlete_data[2],
        'created_at': athlete_data[3]
    }
    return athlete

@router.get("/athlete_by_user_id/{user_id}/")
async def get_athlete_by_user_id(user_id: int):
    athlete_data = await AthletesDAO.get_athlete_info_by_user_id(int(user_id))
    athlete = {
        'id': athlete_data[0],
        'userId': athlete_data[1],
        'trainerId': athlete_data[2],
        'created_at': athlete_data[3]
    }
    return athlete

@router.get("/additional_info/{user_id}/")
async def get_additional_info_by_user_id(user_id: int):
    return await AthletesDAO.get_additional_info(user_id)

@router.post("/additional_info/")
async def set_additional_info(additional_info: SAdditionalInfo):
    additional_info_dict = additional_info.dict()
    print(additional_info_dict)
    await AthletesDAO.set_additional_info(**additional_info_dict)

@router.get("/my_competitions/")
async def get_additional_info_by_user_id(token: str = Depends(get_token)):
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')
    user_id = payload.get('sub')
    athlete_data = await AthletesDAO.get_athlete_info_by_user_id(int(user_id))
    athlete_id = athlete_data[0]
    return await AthletesDAO.get_competition(athlete_id)