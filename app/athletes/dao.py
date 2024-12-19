from app.database import async_session_maker
from sqlalchemy import text


class AthletesDAO:
    @classmethod
    async def get_additional_info(cls, user_id: int):
        async with async_session_maker() as session:
            query = text(f'''
                SELECT 
                    athletes.id as athlete_id,
                    additionalInfo.age as age,
                    additionalInfo.weight as weight,
                    additionalInfo.height as height,
                    additionalInfo.created_at AS additional_info_created_at
                FROM 
                    users
                JOIN 
                    athletes ON users.id = athletes.userId
                LEFT JOIN 
                    additionalInfo ON athletes.id = additionalInfo.athleteId
                WHERE 
                    users.id = :user_id;
            ''')
            result = await session.execute(query, {'user_id': user_id})
            result_data = result.fetchone()
            data = {
                'athlete_id': result_data[0],
                'age': result_data[1],
                'weight': result_data[2],
                'height': result_data[3]
            }
            return data

    @classmethod
    async def subscribe_by_id(cls, athlete_id, trainer_id):
        async with async_session_maker() as session:
            query = text(f'''
                UPDATE athletes 
                SET trainerId = (SELECT id
                FROM trainers
                WHERE userId = :trainer_id)
            ''')
            await session.execute(query, {'athlete_id': athlete_id, 'trainer_id': trainer_id})
            await session.commit()

    @classmethod
    async def get_plans_by_user_id(cls, user_id):
        async with async_session_maker() as session:
            query = text(f'''
                SELECT *
                FROM plans
                WHERE athleteId =(
                    SELECT id
                    FROM athletes
                    WHERE userId = :user_id
                )
                ORDER BY created_at DESC
            ''')
            result = await session.execute(query, {'user_id': user_id})
            plans = [
                {
                    "id": row[0],
                    "athleteId": row[1],
                    "data": row[2],
                    "created_at": row[3]
                }
                for row in result.fetchall()
            ]
            return plans

    @classmethod
    async def get_athlete_info_by_user_id(cls, user_id):
        async with async_session_maker() as session:
            query = text(f'''
                SELECT *
                FROM athletes
                WHERE userId = :user_id
            ''')
            result = await session.execute(query, {'user_id': user_id})
            return result.fetchone()

    @classmethod
    async def set_additional_info(cls, **values):
        async with async_session_maker() as session:
            age = values.get('age')
            weight = values.get('weight')
            height = values.get('height')
            athlete_id = values.get('athleteId')
            query = text(f'''
                UPDATE additionalInfo
                SET age = :age, weight = :weight, height = :height
                WHERE athleteId = :athlete_id
            ''')
            await session.execute(query, {'age': age, 'weight': weight, 'height': height, 'athlete_id': athlete_id})
            await session.commit()

    @classmethod
    async def get_competition(cls, athlete_id: int):
        async with async_session_maker() as session:
            query = text('''
                SELECT c.id, c.title as title, c.data as data
                FROM competitions c
                JOIN competitionsAthleteLinks cal ON c.id = cal.competitionId
                WHERE cal.athleteId = :athlete_id
            ''')
            result = await session.execute(query, {'athlete_id': athlete_id})
            data = [
                {
                'title': row[1],
                'data': row[2]
                }
                for row in result.fetchall()
            ]
            return data

