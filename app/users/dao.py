from app.database import async_session_maker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text


class UsersDAO:
    @classmethod
    async def find_one_or_none_by_id(cls, data_id: int):
        async with async_session_maker() as session:
            query = text(f"SELECT * FROM users WHERE id = :data_id")
            result = await session.execute(query, {"data_id": data_id})
            return result.fetchone()

    @classmethod
    async def addUser(cls, **values):
        async with async_session_maker() as session:
            async with session.begin():
                try:
                    user_values = {
                        "first_name": values.get("first_name"),
                        "last_name": values.get("last_name"),
                        "phone_number": values.get("phone_number"),
                        "password": values.get("password"),
                        "role": values.get("role"),
                    }
                    insert_user_stmt = text("""
                        INSERT INTO users (first_name, last_name, phone_number, password, role)
                        VALUES (:first_name, :last_name, :phone_number, :password, :role)    
                    """)
                    await session.execute(insert_user_stmt, user_values)
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e

    @classmethod
    async def get_role(cls, userId: int):
        async with async_session_maker() as session:
            async with session.begin():
                query = text("""
                    SELECT r.*
                    FROM roles r
                    JOIN usersRolesLinks url ON r.id = url.roleId
                    WHERE url.userId = :userId
                """)
                result = await session.execute(query, {"userId": userId})
                return result.all()

