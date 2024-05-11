from datetime import datetime as dt

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from errors import DatabaseError, InvalidDateError, LocationExistsError
from .models import Trip


async def add_location_db(
    data: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    """
    Add a new location to the trip.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                trip = await session.get(Trip, data["trip_id"])
                locations = list(trip.locations)
                start_date = data["start_date"]
                end_date = data["end_date"]

                if locations:
                    existing_locations = list(
                        map(lambda x: (x["latitude"], x["longitude"]), locations)
                    )

                    if (data["latitude"], data["longitude"]) not in existing_locations:
                        previous_end_date = dt.strptime(
                            locations[-1]["end_date"], "%d.%m.%Y"
                        )

                        if start_date >= previous_end_date:
                            data["start_date"] = start_date.strftime("%d.%m.%Y")
                            data["end_date"] = end_date.strftime("%d.%m.%Y")
                            locations.append(data)
                        else:
                            raise InvalidDateError
                    else:
                        raise LocationExistsError
                else:
                    data["start_date"] = start_date.strftime("%d.%m.%Y")
                    data["end_date"] = end_date.strftime("%d.%m.%Y")
                    locations.append(data)

                trip.locations = locations

            except InvalidDateError:
                await session.rollback()
                raise InvalidDateError
            except LocationExistsError:
                await session.rollback()
                raise LocationExistsError
            except:
                await session.rollback()
                raise DatabaseError


async def get_location_db(
    trip_id: int,
    latitude: float,
    longitude: float,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> dict:
    """
    Get the location from the trip.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                trip = await session.get(Trip, trip_id)
                locations = list(trip.locations)
                location = tuple(
                    filter(
                        lambda x: x["latitude"] == latitude
                        and x["longitude"] == longitude,
                        locations,
                    )
                )[0]

                return location
            except:
                await session.rollback()
                raise DatabaseError


async def delete_location_db(
    trip_id: int,
    latitude: float,
    longitude: float,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    """
    Remove the location from the trip.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                trip = await session.get(Trip, trip_id)
                locations = list(trip.locations)
                location = tuple(
                    filter(
                        lambda x: x["latitude"] == latitude
                        and x["longitude"] == longitude,
                        locations,
                    )
                )[0]

                locations.remove(location)
                trip.locations = locations

            except:
                await session.rollback()
                raise DatabaseError
