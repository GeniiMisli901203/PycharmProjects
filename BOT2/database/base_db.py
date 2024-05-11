from rapidfuzz import fuzz, utils
from sqlalchemy import select, or_, and_, not_, desc, func
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from errors import DatabaseError
from .models import *


async def get_items(
    user: dict,
    offset: int,
    source_type: str,
    sessionmaker: async_sessionmaker[AsyncSession],
    trip_id: int | None = None,
    expense_id: int | None = None,
) -> tuple[list, int]:
    """
    Get items from the db.
    """

    right_ind = offset + 5

    async with sessionmaker() as session:
        async with session.begin():
            try:
                match source_type:
                    case "trips":
                        res = []
                        trips = await session.execute(
                            select(Trip)
                            .filter(
                                or_(
                                    and_(
                                        Trip.username == user["username"],
                                        not_(Trip.friends.contains([user["username"]])),
                                    ),
                                    and_(
                                        Trip.username != user["username"],
                                        Trip.friends.contains([user["username"]]),
                                    ),
                                )
                            )
                            .order_by(desc(Trip.id))
                            .offset(offset)
                        )

                        for trip in trips.scalars().all():
                            if user["username"] in trip.friends:
                                res.append((f"\U0001F517 {trip.name}", trip.id))
                            else:
                                res.append((trip.name, trip.id))

                        if right_ind < len(res):
                            res = res[:right_ind]

                        pages = res

                    case "notes":
                        res = []
                        notes = await session.execute(
                            select(Note)
                            .filter(Note.trip_id == trip_id)
                            .order_by(desc(Note.id))
                            .offset(offset)
                        )

                        for note in notes.scalars().all():
                            if note.user_id != user["id"] and not note.is_private:
                                res.append((f"\U0001F517 {note.name}", note.id))
                            elif note.user_id == user["id"]:
                                res.append((note.name, note.id))

                        if right_ind < len(res):
                            res = res[:right_ind]

                        pages = res

                    case "friends":
                        trip = await session.get(Trip, trip_id)
                        friends = trip.friends

                        friends_accounts = (
                            (
                                await session.execute(
                                    select(User)
                                    .filter(User.username.in_(list(friends)))
                                    .order_by(User.username)
                                    .offset(offset)
                                )
                            )
                            .scalars()
                            .all()
                        )

                        if right_ind < len(friends_accounts):
                            res_friends = friends_accounts[:right_ind]
                        else:
                            res_friends = friends_accounts

                        pages = friends_accounts

                        res = [user.username for user in res_friends]

                    case "find_friends":
                        right_ind = offset + 5
                        trip = await session.get(Trip, trip_id)
                        users = (
                            (
                                await session.execute(
                                    select(User)
                                    .filter(
                                        func.abs(User.age - user["age"]) <= 5,
                                        User.id != user["id"],
                                        not_(User.username.in_(list(trip.friends))),
                                    )
                                    .order_by(User.username)
                                    .offset(offset)
                                )
                            )
                            .scalars()
                            .all()
                        )

                        if not users:
                            return [], 0

                        to_sort = []

                        for found_user in users:
                            ratio = fuzz.ratio(
                                found_user.bio,
                                user["bio"],
                                processor=utils.default_process,
                            )

                            if ratio >= 25:
                                to_sort.append((ratio, found_user.username))

                        to_sort.sort(key=lambda x: x[0], reverse=True)

                        if right_ind < len(users):
                            res_users = to_sort[:right_ind]
                        else:
                            res_users = to_sort

                        pages = to_sort

                        res = [username for _, username in res_users]

                    case "locations":
                        locations = (
                            (
                                await session.execute(
                                    select(Trip).filter(Trip.id == trip_id)
                                )
                            )
                            .scalar_one()
                            .locations
                        )

                        if right_ind >= len(locations):
                            res_locations = list(locations)[offset:]
                        else:
                            res_locations = list(locations)[offset:right_ind]

                        pages = locations[offset:]
                        res = [
                            (
                                location["country"],
                                location["city"],
                                location["latitude"],
                                location["longitude"],
                            )
                            for location in res_locations
                        ]

                    case "expenses":
                        expenses = (
                            (
                                await session.execute(
                                    select(Expense)
                                    .filter(Expense.trip_id == trip_id)
                                    .order_by(Expense.date)
                                    .offset(offset)
                                )
                            )
                            .scalars()
                            .all()
                        )

                        res = []

                        for expense in expenses:
                            if user["username"] in expense.debtors:
                                res.append((f"\U00002757 {expense.name}", expense.id))
                            elif user["username"] == expense.username:
                                res.append((expense.name, expense.id))

                        if right_ind < len(expenses):
                            res = res[:right_ind]

                        pages = res

                    case "expense_debtors":
                        res = (
                            (
                                await session.execute(
                                    select(Expense).filter(Expense.id == expense_id)
                                )
                            )
                            .scalar_one()
                            .debtors
                        )

                        if right_ind < len(res):
                            res = res[:right_ind]

                        pages = res

                return res, (len(pages) - 1) // 5 if len(pages) >= 1 else 0
            except:
                await session.rollback()
                raise DatabaseError
