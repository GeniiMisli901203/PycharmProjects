from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from errors import DatabaseError
from .models import Trip


async def create_update_trip(
    data: dict, sessionmaker: async_sessionmaker[AsyncSession]
) -> None:
    """
    Create or update the trip in the db.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                if "locations" in data:
                    data["locations"][0]["start_date"] = data["dates"][0]
                    data["locations"][0]["end_date"] = data["dates"][1]
                    data.pop("dates")

                if "id" in data:
                    trip_id = data["id"]
                    data.pop("id")

                    if data:
                        await session.execute(
                            update(Trip).filter(Trip.id == trip_id).values(**data)
                        )
                else:
                    trip = Trip(**data)
                    session.add(trip)
            except:
                await session.rollback()
                raise DatabaseError


async def get_trip_db(
    trip_id: int, sessionmaker: async_sessionmaker[AsyncSession]
) -> dict:
    """
    Get the trip info from the db.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                trip = await session.get(Trip, trip_id)
                return trip.columns_to_dict()
            except:
                await session.rollback()
                raise DatabaseError


async def delete_trip_db(
    trip_id: int, sessionmaker: async_sessionmaker[AsyncSession]
) -> None:
    """
    Delete the trip in the db.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                await session.execute(delete(Trip).filter(Trip.id == trip_id))
            except:
                await session.rollback()
                raise DatabaseError
