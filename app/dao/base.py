from sqlalchemy.exc import SQLAlchemyError
from app.database import async_session_maker
from sqlalchemy import text


async def find_one_or_none(table_name: str, **filter_by):
    async with async_session_maker() as session:
        filter_conditions = " AND ".join(f"{key} = :{key}" for key in filter_by)
        query = text(f"SELECT * FROM {table_name} WHERE {filter_conditions}")
        result = await session.execute(query, filter_by)
        return result.fetchone()

async def add_in_table(table_name: str, **values):
    async with async_session_maker() as session:
        async with session.begin():
            columns = ", ".join(values.keys())
            placeholders = ", ".join(f":{key}" for key in values.keys())
            query = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING *")
            result = await session.execute(query, values)
            row = result.fetchone()
            try:
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e
            return row

