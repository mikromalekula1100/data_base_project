import sqlparse
import asyncio

from app.database import async_session_maker
from app.config import get_path_ddl
from sqlalchemy import text

async def init_db():
    async with async_session_maker() as session:
        async with session.begin():
            list_files = [get_path_ddl()]
            for f in list_files:
                with open(f, 'r') as file:
                    sql_script = file.read()
                sql_commands = sqlparse.split(sql_script)
                for command in sql_commands:
                    command = command.strip()
                    if command:
                        await session.execute(text(command))


if __name__ == "__main__":
    asyncio.run(init_db())
