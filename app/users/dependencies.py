from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError
from app.config import get_auth_data
from app.users.dao import UsersDAO
from app.users.models import User


def get_token(request: Request):
    token = request.cookies.get('users_access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    return token

async def get_current_user(token: str = Depends(get_token)):
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')
    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не найден ID пользователя')
    user_data = await UsersDAO.find_one_or_none_by_id(int(user_id))
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    user = {
        'id': user_data[0],
        'first_name': user_data[1],
        'last_name': user_data[2],
        'phone_number': user_data[3],
        'password': user_data[4],
        'role': user_data[5],
        'created_at': user_data[6],
        'update_at': user_data[7]
    }
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав!')




