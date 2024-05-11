from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from errors import DatabaseError, UserNotFoundError
from .models import User, Trip


async def add_friend_db(
    username: str,
    trip_id: int,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> tuple[str, int]:
    """
    Add user's friend to the trip and get his id.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                user = (
                    await session.execute(
                        select(User).filter(User.username == username)
                    )
                ).scalar_one_or_none()

                if not user:
                    raise UserNotFoundError

                trip = await session.get(Trip, trip_id)
                friends = list(trip.friends)

                if username not in friends:
                    friends.append(username)

                trip.friends = friends
                return trip.name, user.id

            except UserNotFoundError:
                await session.rollback()
                raise UserNotFoundError
            except:
                await session.rollback()
                raise DatabaseError


async def remove_friend_db(
    username: str,
    trip_id: int,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    """
    Remove the friend from the trip.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                trip = await session.get(Trip, trip_id)
                friends = list(trip.friends)
                if username in friends:
                    friends.remove(username)
                trip.friends = friends
            except:
                await session.rollback()
                raise DatabaseError
