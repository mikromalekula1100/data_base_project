from fastapi import APIRouter, HTTPException, status, Response, Depends
from app.users.auth import get_password_hash, authenticate_user, create_access_token
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user
from app.users.schemas import SUserRegister, SUserAuth
from app.dao.base import find_one_or_none
from app.users.models import User
from app.config import get_auth_data
from jose import jwt, JWTError
from app.users.dependencies import get_token


router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post("/register/")
async def register_user(user_data: SUserRegister) -> dict:
    user = await find_one_or_none("users", phone_number=user_data.phone_number)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь уже существует'
        )
    user_dict = user_data.dict()
    user_dict['password'] = get_password_hash(user_data.password)
    await UsersDAO.addUser(**user_dict)
    return {'message': 'Вы успешно зарегистрированы!'}

@router.post("/login/")
async def auth_user(response: Response, user_data: SUserAuth):
    check = await authenticate_user(phone_number=user_data.phone_number, password=user_data.password)
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверный номер или пароль')

    access_token = create_access_token({"sub": str(check.id), "role": check.role})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'access_token': access_token, 'refresh_token': None}

@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}

@router.get("/me/")
async def get_me(user_data: User = Depends(get_current_user)):
    return user_data

@router.get("/token_correct/")
async def token_is_correct(token: str = Depends(get_token)):
     try:
         auth_data = get_auth_data()
         jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
     except JWTError:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')
     return True
