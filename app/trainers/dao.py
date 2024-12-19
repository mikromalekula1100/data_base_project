from app.database import async_session_maker
from sqlalchemy import text


class TrainersDAO:
    @classmethod
    async def get_all_trainers(cls):
        async with async_session_maker() as session:
            query = text(f'''
                SELECT * 
                FROM users
                WHERE id in (SELECT userId FROM trainers)
            ''')
            result = await session.execute(query)
            trainers = [
                {
                    "id": row[0],  # Индексы зависят от порядка столбцов в SELECT
                    "first_name": row[1],
                    "last_name": row[2],
                    "phone_number": row[3],
                    "password": row[4],
                    "role": row[5],
                    "created_at": row[6],
                    "updated_at": row[7],
                }
                for row in result.fetchall()
            ]
            return trainers

    @classmethod
    async def get_signed_athletes(cls, trainer_id: int):
        async with async_session_maker() as session:
            query = text(f'''
                    SELECT *
                    FROM users
                    WHERE id IN (
                        SELECT userId
                        FROM athletes
                        WHERE trainerId = (
                            SELECT id
                            FROM trainers
                            WHERE userId = :trainer_id
                        )
                    )
            ''')
            result = await session.execute(query, {'trainer_id': trainer_id})
            athletes = [
                {
                    "id": row[0],  # Индексы зависят от порядка столбцов в SELECT
                    "first_name": row[1],
                    "last_name": row[2],
                    "phone_number": row[3],
                    "password": row[4],
                    "role": row[5],
                    "created_at": row[6],
                    "updated_at": row[7],
                }
                for row in result.fetchall()
            ]
            return athletes


    @classmethod
    async def get_user_info_by_trainer_id(cls, trainer_id: int):
        async with async_session_maker() as session:
            query = text(f'''
                SELECT *
                FROM users
                WHERE id = (
                    SELECT userId
                    FROM trainers
                    WHERE id = :trainer_id
                )            
            ''')
            result = await session.execute(query, {'trainer_id': trainer_id})
            data = result.fetchone()

            user_data = {
                'id': data[0],
                'first_name': data[1],
                'last_name': data[2],
                'phone_number': data[3],
                'password': data[4],
                'role': data[5],
                'created_at': data[6],
                'updated_at': data[7],
            }
            return user_data

    @classmethod
    async def get_trainer_id_by_user_id_trainer(cls, user_id):
        async with async_session_maker() as session:
            query = text(f'''
                SELECT id
                FROM trainers
                WHERE userId = :user_id
            ''')
            result = await session.execute(query, {'user_id': user_id})
            return result.fetchone()[0]

    @classmethod
    async def get_trainer_id_by_user_id_athlete(cls, user_id):
        async with async_session_maker() as session:
            query = text(f'''
                SELECT trainerId
                FROM athletes
                WHERE id = (
                    SELECT id
                    FROM athletes
                    WHERE userId = :user_id
                )
            ''')
            result = await session.execute(query, {'user_id': user_id})
            return result.fetchone()[0]


    @classmethod
    async def get_all_reports_by_trainer_id(cls, trainer_id: int):
        async with async_session_maker() as session:
            query = text(f'''
                SELECT 
                    reports.id AS report_id,
                    reports.data AS report_data,
                    reports.created_at AS report_created_at,
                    plans.id AS plan_id,
                    plans.data AS plan_data,
                    plans.created_at as plan_created_time,
                    athletes.id AS athlete_id,
                    users.first_name AS athlete_first_name,
                    users.last_name AS athlete_last_name,
                    users.phone_number AS athlete_phone_number,
                    users.role AS athlete_role,
                    users.created_at AS user_created_at
                FROM reports
                JOIN plans ON reports.planId = plans.id
                JOIN athletes ON plans.athleteId = athletes.id
                JOIN users ON athletes.userId = users.id
                WHERE reports.trainerId = :trainer_id
                ORDER BY report_created_at DESC
            ''')
            result = await session.execute(query, {'trainer_id': trainer_id})
            reports = [
                {
                    "report_id": row[0],
                    "report_data": row[1],
                    "report_created_at": row[2],
                    "plan_id": row[3],
                    "plan_data": row[4],
                    "plan_created_time": row[5],
                    "athlete_id": row[6],
                    "athlete_first_name": row[7],
                    "athlete_last_name": row[8],
                    "athlete_phone_number": row[9],
                    "athlete_role": row[10],
                    "user_created_at": row[11]
                }
                for row in result.fetchall()
            ]
            return reports

    @classmethod
    async def get_all_competitions(cls, trainer_id):
        async with async_session_maker() as session:
            query = text(f'''
            SELECT 
                trainers.id AS trainer_id,
                users.first_name AS trainer_first_name,
                users.last_name AS trainer_last_name,
                athletes.id AS athlete_id,
                athlete_users.first_name AS athlete_first_name,
                athlete_users.last_name AS athlete_last_name,
                competitions.id AS competition_id,
                competitions.title AS competition_title,
                competitions.data AS competition_data
            FROM 
                trainers
            JOIN 
                users ON trainers.userId = users.id
            LEFT JOIN 
                athletes ON athletes.trainerId = trainers.id
            LEFT JOIN 
                users AS athlete_users ON athletes.userId = athlete_users.id
            LEFT JOIN 
                competitionsAthleteLinks ON competitionsAthleteLinks.athleteId = athletes.id
            LEFT JOIN 
                competitions ON competitions.id = competitionsAthleteLinks.competitionId
            WHERE 
                trainers.id = :trainer_id
                AND competitions.title IS NOT NULL
                AND competitions.data IS NOT NULL
            ''')
            result = await session.execute(query, {'trainer_id': trainer_id})

            competitions = [
                {
                    'athlete_first_name': row[4],
                    'athlete_last_name': row[5],
                    'competition_title': row[7] if row[7] is not None else "Нет данных",
                    'competition_data': row[8] if row[8] is not None else "Нет данных",
                }
                for row in result.fetchall()
            ]
            return competitions




