from asyncio import BoundedSemaphore

import aiofiles.os as aos
from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, FSInputFile
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from states import FSMNote
from errors import DatabaseError
from config_data import Config, load_config
from lexicon import LEXICON_RU, ERROR_LEXICON_RU
from database import add_note_db, get_note_db, delete_note_db
from keyboards import (
    paginator_kb,
    private_kb,
    base_note_kb,
    base_notes_kb,
    confirm_note_deletion_kb,
    back_to_notes_kb,
)


note_router: Router = Router()
config: Config = load_config()
semaphore: BoundedSemaphore = config.tg_bot.semaphore


@note_router.callback_query(
    F.data.func(lambda x: "notes-" in x and "-page-" in x),
    StateFilter(default_state),
)
async def notes(
    callback: CallbackQuery,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Send active trips.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")

        await callback.message.answer(
            LEXICON_RU["my_notes"],
            reply_markup=(
                await paginator_kb(
                    user, int(data[-1]), "notes", sessionmaker, trip_id=int(data[1])
                )
            ),
        )
    except:
        await callback.message.answer(ERROR_LEXICON_RU["InternalError"])


@note_router.callback_query(
    F.data.func(lambda x: "-new-note" in x), StateFilter(default_state)
)
async def new_note(callback: CallbackQuery, state: FSMContext):
    """
    Let the user select if the new note is private.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")

        await callback.message.edit_text(
            LEXICON_RU["new_note"], reply_markup=private_kb()
        )
        await state.update_data(trip_id=int(data[1]))
        await state.set_state(FSMNote.set_private)
    except:
        await state.clear()
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@note_router.callback_query(
    F.data.in_(("private_note", "unprivate_note")),
    StateFilter(FSMNote.set_private),
)
async def private_note(callback: CallbackQuery, state: FSMContext):
    """
    Set if note is private and let the user upload the note file.
    """

    try:
        await callback.answer()
        await callback.message.edit_text(LEXICON_RU["upload_file"])
        await state.update_data(is_private=callback.data)
        await state.set_state(FSMNote.set_note)
    except:
        await state.clear()
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@note_router.message(StateFilter(FSMNote.set_note))
async def upload_note(
    message: Message,
    state: FSMContext,
    user: dict,
    bot: Bot,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Upload the new note.
    """

    try:
        data = await state.get_data()
        trip_id = data["trip_id"]
        src = f"./files/{user["id"]}/{trip_id}/"
        await aos.makedirs(src, exist_ok=True)

        async with semaphore:
            if message.photo:
                file = message.photo[-1]
                destination = src + f"фото-{file.file_unique_id}"
                file_type = "photo"
            elif message.animation:
                file = message.animation
                destination = src + f"анимация-{file.file_name}"
                file_type = "animation"
                data["width"] = file.width
                data["height"] = file.height
            elif message.audio:
                file = message.audio
                destination = src + f"аудио-{file.file_name}"
                file_type = "audio"
            elif message.video_note:
                file = message.video_note
                destination = src + f"кружок-{file.file_unique_id}"
                file_type = "video_note"
            elif message.video:
                file = message.video
                destination = src + f"видео-{file.file_name}"
                file_type = "video"
                data["width"] = file.width
                data["height"] = file.height
            elif message.voice:
                file = message.voice
                destination = src + f"голос-{file.file_unique_id}"
                file_type = "voice"
            elif message.document:
                file = message.document
                destination = src + f"документ-{file.file_name}"
                file_type = "document"

            await bot.download(file, destination)

        data["user_id"] = user["id"]
        data["path"] = destination
        data["file_type"] = file_type

        await message.answer(
            LEXICON_RU["uploading_done"], reply_markup=base_notes_kb(trip_id)
        )
        await add_note_db(data, sessionmaker)
        await state.clear()

    except DatabaseError:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await state.clear()
        await message.answer(
            ERROR_LEXICON_RU["incorrect_file"],
            reply_markup=base_notes_kb(trip_id),
        )


@note_router.callback_query(
    F.data.func(lambda x: "-note-" in x and "notes-" in x and x.count("-") == 3),
    StateFilter(default_state),
)
async def get_note(
    callback: CallbackQuery,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Send the note with delete button.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        trip_id = int(data[1])
        note_id = int(data[-1])
        note = await get_note_db(note_id, sessionmaker)
        file = FSInputFile(note["path"])
        caption = note["name"]

        async with semaphore:
            match note["file_type"]:
                case "photo":
                    await callback.message.answer_photo(
                        file,
                        caption=caption,
                        reply_markup=base_note_kb(
                            trip_id,
                            note_id,
                            user["id"] == note["user_id"],
                        ),
                    )
                case "animation":
                    await callback.message.answer_animation(
                        file,
                        width=note["width"],
                        height=note["height"],
                        caption=caption,
                        reply_markup=base_note_kb(
                            trip_id,
                            note_id,
                            user["id"] == note["user_id"],
                        ),
                    )
                case "audio":
                    await callback.message.answer_audio(
                        file,
                        caption=caption,
                        reply_markup=base_note_kb(
                            trip_id,
                            note_id,
                            user["id"] == note["user_id"],
                        ),
                    )
                case "video_note":
                    await callback.message.answer_video_note(
                        file,
                        caption=caption,
                        reply_markup=base_note_kb(
                            trip_id,
                            note_id,
                            user["id"] == note["user_id"],
                        ),
                    )
                case "video":
                    await callback.message.answer_video(
                        file,
                        width=note["width"],
                        height=note["height"],
                        caption=caption,
                        reply_markup=base_note_kb(
                            trip_id,
                            note_id,
                            user["id"] == note["user_id"],
                        ),
                    )
                case "voice":
                    await callback.message.answer_voice(
                        file,
                        caption=caption,
                        reply_markup=base_note_kb(
                            trip_id,
                            note_id,
                            user["id"] == note["user_id"],
                        ),
                    )
                case "document":
                    await callback.message.answer_document(
                        file,
                        caption=caption,
                        reply_markup=base_note_kb(
                            trip_id,
                            note_id,
                            user["id"] == note["user_id"],
                        ),
                    )
    except:
        await callback.message.answer(ERROR_LEXICON_RU["InternalError"])


@note_router.callback_query(
    F.data.func(lambda x: "pre-delete-notes-" in x), StateFilter(default_state)
)
async def pre_delete_note(callback: CallbackQuery):
    """
    Let the user delete the note.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        await callback.message.answer(
            LEXICON_RU["confirm_deletion"],
            reply_markup=confirm_note_deletion_kb(int(data[3]), int(data[-1])),
        )
    except:
        await callback.message.answer(ERROR_LEXICON_RU["InternalError"])


@note_router.callback_query(
    F.data.func(lambda x: "finally-delete-notes-" in x), StateFilter(default_state)
)
async def finally_delete_note(
    callback: CallbackQuery,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    try:
        await callback.answer()
        data = callback.data.split("-")
        trip_id = int(data[3])
        note_id = int(data[-1])
        path = await delete_note_db(note_id, sessionmaker)
        await callback.message.edit_text(
            LEXICON_RU["deletion_done"],
            reply_markup=back_to_notes_kb(trip_id),
        )

        async with semaphore:
            if await aos.path.isfile(path):
                await aos.remove(path)

    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@note_router.callback_query(
    F.data.func(lambda x: "cancel-notes-" in x),
    StateFilter(default_state),
)
async def cancel_note_deletion(callback: CallbackQuery):
    try:
        await callback.answer()
        data = callback.data.split("_")
        await callback.message.edit_text(
            LEXICON_RU["deletion_canceled"],
            reply_markup=back_to_notes_kb(int(data[2])),
        )
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])
