from app.database import async_session_maker
from sqlalchemy import text

class ReportDAO:
    @classmethod
    async def add_report(cls, **values):
        async with async_session_maker() as session:
            trainer_id = values.get("trainer_id")
            data = values.get("data")
            plan_id = values.get("plan_id")
            query = text(f'''
                INSERT INTO reports (trainerId, data, planId)
                VALUES (:trainer_id, :data, :plan_id)
            ''')
            await session.execute(
                query,
                {"trainer_id": trainer_id, "data": data, "plan_id": plan_id}
            )
            await session.commit()