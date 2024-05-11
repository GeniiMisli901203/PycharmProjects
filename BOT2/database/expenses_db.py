from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from errors import DatabaseError, UserNotFoundError, UserNotInTripError
from .models import User, Trip, Expense


async def create_update_expense_db(
    data: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> tuple[list, str] | int:
    """
    Add expense to the trip and return debtor's IDs and trip name or update it and return trip ID.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                if "expense_id" not in data:
                    debtors = []

                    for friend in data["debtors"]:
                        user = (
                            await session.execute(
                                select(User).filter(User.username == friend)
                            )
                        ).scalar_one_or_none()
                        trip = await session.get(Trip, data["trip_id"])

                        if not user:
                            raise UserNotFoundError
                        elif user.username not in [trip.username, *trip.friends]:
                            raise UserNotInTripError
                        else:
                            debtors.append(user.id)

                        expense = Expense(**data)
                        session.add(expense)
                        return debtors, trip.name
                else:
                    expense = await session.get(Expense, data["expense_id"])
                    data.pop("expense_id")

                    if data:
                        await session.execute(
                            update(Expense)
                            .filter(Expense.id == expense.id)
                            .values(**data)
                        )
                    return expense.trip_id

            except UserNotFoundError:
                await session.rollback()
                raise UserNotFoundError
            except UserNotInTripError:
                await session.rollback()
                raise UserNotInTripError
            except:
                await session.rollback()
                raise DatabaseError


async def get_expense_db(
    expense_id: int, sessionmaker: async_sessionmaker[AsyncSession]
) -> dict:
    """
    Get the expense from the db.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                expense = await session.get(Expense, expense_id)
                return expense.columns_to_dict()
            except:
                await session.rollback()
                raise DatabaseError


async def add_debtor_db(
    data: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> tuple[int, str, int]:
    """
    Add debtor to the expense and return his ID, trip name and trip ID.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                username = data["debtor"]
                user = (
                    await session.execute(
                        select(User).filter(User.username == username)
                    )
                ).scalar_one_or_none()
                expense = await session.get(Expense, data["expense_id"])
                trip = await session.get(Trip, expense.trip_id)

                if not user:
                    raise UserNotFoundError
                elif user.username not in trip.friends:
                    raise UserNotInTripError

                debtors = list(expense.debtors)

                if username not in debtors:
                    debtors.append(username)

                expense.debtors = debtors
                return user.id, trip.name, trip.id

            except UserNotFoundError:
                await session.rollback()
                raise UserNotFoundError
            except UserNotInTripError:
                await session.rollback()
                raise UserNotInTripError
            except:
                await session.rollback()
                raise DatabaseError


async def delete_expense_db(
    expense_id: int, sessionmaker: async_sessionmaker[AsyncSession]
) -> None:
    """
    Delete the expense in the db.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                await session.execute(delete(Expense).filter(Expense.id == expense_id))
            except:
                await session.rollback()
                raise DatabaseError


async def write_off_debt_db(
    username: str,
    expense_id: int,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> tuple[int, bool]:
    """
    Write off the debts in expense and
    return trip ID and True if expense is closed.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                expense = await session.get(Expense, expense_id)
                debtors = list(expense.debtors)
                trip_id = expense.trip_id
                expense.cost -= round(expense.cost / len(debtors), 2)

                if expense.cost == 0:
                    await session.execute(
                        delete(Expense).filter(Expense.id == expense_id)
                    )
                    return trip_id, True

                if username in debtors:
                    debtors.remove(username)

                expense.debtors = debtors
                return trip_id, False

            except:
                await session.rollback()
                raise DatabaseError


async def loser_db(
    username: str,
    expense_id: int,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    """
    Сredit all debts to in expense to loser.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                expense = await session.get(Expense, expense_id)

                if username == expense.username:
                    await session.execute(
                        delete(Expense).filter(Expense.id == expense_id)
                    )
                else:
                    expense.debtors = [username]

            except:
                await session.rollback()
                raise DatabaseError
