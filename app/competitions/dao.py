from app.database import async_session_maker
from sqlalchemy import text


class CompetitionDAO:
    @classmethod
    async def add_competition_by_athlete_id(cls, athlete_id: int, **values):
        async with async_session_maker() as session:
            try:
                title = values.get('title')
                data = values.get('data')
                insert_competition_query = text('''
                    INSERT INTO competitions (title, data)
                    VALUES (:title, :data)
                    RETURNING id;
                ''')
                result = await session.execute(insert_competition_query, {'title': title, 'data': data})
                competition_id = result.scalar()
                insert_link_query = text('''
                    INSERT INTO competitionsAthleteLinks (competitionId, athleteId)
                    VALUES (:competition_id, :athlete_id);
                ''')
                await session.execute(insert_link_query, {'competition_id': competition_id, 'athlete_id': athlete_id})
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e