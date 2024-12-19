from fastapi import APIRouter, Depends
from app.reports.dao import ReportDAO
from app.reports.schemas import SReports
from fastapi import APIRouter
from app.users.dependencies import get_token
from fastapi import HTTPException, status, Depends
from jose import jwt, JWTError
from app.config import get_auth_data
from app.trainers.dao import TrainersDAO


router = APIRouter(prefix='/reports', tags=['Reports'])

@router.post("/report/")
async def add_report(report_data: SReports, token: str = Depends(get_token)):
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')
    user_id = payload.get('sub')
    trainer_id = await TrainersDAO.get_trainer_id_by_user_id_athlete(int(user_id))
    report = {
        'trainer_id': int(trainer_id),
        'plan_id': report_data.planId,
        'data': report_data.data
    }
    await ReportDAO.add_report(**report)