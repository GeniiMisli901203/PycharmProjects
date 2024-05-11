from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from errors import DatabaseError
from .models import Note


async def add_note_db(
    data: dict, sessionmaker: async_sessionmaker[AsyncSession]
) -> None:
    """
    Add note to the trip.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                name = data["path"].split("/")[-1]
                private = False

                if data["is_private"] == "private_note":
                    private = True

                width = data.get("width")
                height = data.get("height")

                note = Note(
                    user_id=data["user_id"],
                    trip_id=data["trip_id"],
                    name=name,
                    path=data["path"],
                    file_type=data["file_type"],
                    width=width,
                    height=height,
                    is_private=private,
                )

                session.add(note)
            except:
                await session.rollback()
                raise DatabaseError


async def get_note_db(
    note_id: int, sessionmaker: async_sessionmaker[AsyncSession]
) -> dict:
    """
    Get the note from the db.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                note = await session.get(Note, note_id)
                return note.columns_to_dict()
            except:
                await session.rollback()
                raise DatabaseError


async def delete_note_db(
    note_id: int, sessionmaker: async_sessionmaker[AsyncSession]
) -> str:
    """
    Delete the note in the db.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                note = await session.get(Note, note_id)
                await session.execute(delete(Note).filter(Note.id == note_id))
                return note.path
            except:
                await session.rollback()
                raise DatabaseError
