from app.database import async_session_maker
from sqlalchemy import text


class PlanDAO:
    @classmethod
    async def add_plan_by_athlete_id(cls, **values):
        async with async_session_maker() as session:
            athlete_id = values.get("athlete_id")
            plan_payload = values.get("data_plan")
            query = text(f'''
                INSERT INTO plans (athleteId, data) 
                VALUES (:athlete_id, :plan_payload)
            ''')
            await session.execute(
                query,
                {"athlete_id": athlete_id, "plan_payload": plan_payload}
            )
            await session.commit()