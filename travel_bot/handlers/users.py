from cashews import Cache
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, StateFilter
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from states import FSMSettings
from services import create_profile
from config_data import Config, load_config
from database import create_update_user
from errors import DatabaseError, GeocodingError
from external_services import convert_coordinates
from lexicon import LEXICON_RU, KB_LEXICON_RU, ERROR_LEXICON_RU, CURRENCY_DICT
from keyboards import (
    menu_kb,
    set_location_kb,
    leave_same_kb,
    leave_blank_kb,
    edit_kb,
    set_sex_kb,
    set_currency_kb,
)


user_router: Router = Router()
config: Config = load_config()
cache: Cache = config.tg_bot.cache


@user_router.message(CommandStart(), StateFilter(default_state))
async def start_command(message: Message, state: FSMContext):
    """
    Send the start message and
    start the configuration procedure.
    """

    try:
        if not message.from_user.username:
            await message.answer(ERROR_LEXICON_RU["no_username"])
        else:
            await message.answer(LEXICON_RU["start"])
            await state.update_data(
                id=message.from_user.id, username=message.from_user.username
            )
            await state.set_state(FSMSettings.set_age)
    except:
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@user_router.message(Command(commands=["help"]))
async def help_command(message: Message, state: FSMContext):
    await message.answer(LEXICON_RU["help"])
    await state.clear()


@user_router.message(Command(commands=["menu"]))
async def menu_command(message: Message, user: dict | None, state: FSMContext):
    if user:
        await message.answer(LEXICON_RU["menu"], reply_markup=menu_kb())
    else:
        await message.answer(ERROR_LEXICON_RU["no_profile"])
    await state.clear()


@user_router.message(Command(commands=["profile"]))
async def profile_command(message: Message, user: dict | None, state: FSMContext):
    """
    Send the user profile with edit button.
    """

    try:
        if user:
            await message.answer(
                create_profile(user), reply_markup=edit_kb()
            )
        else:
            await message.answer(ERROR_LEXICON_RU["no_profile"])

        await state.clear()
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@user_router.message(F.text, StateFilter(FSMSettings.set_age))
async def profile_age(message: Message, state: FSMContext):
    """
    Set user age and send a message
    which allows the user to set his sex.
    """

    try:
        user_age = int(message.text)

        if user_age not in range(1, 121):
            await message.answer(ERROR_LEXICON_RU["incorrect_data"])
        else:
            await message.answer(LEXICON_RU["set_sex"], reply_markup=set_sex_kb())
            await state.update_data(age=user_age)
            await state.set_state(FSMSettings.set_sex)

    except ValueError:
        await message.answer(ERROR_LEXICON_RU["incorrect_data"])
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@user_router.callback_query(StateFilter(FSMSettings.set_sex))
async def profile_sex(callback: CallbackQuery, state: FSMContext):
    """
    Set user sex and send a message
    which allows the user to set his location.
    """

    try:
        await callback.answer()
        await callback.message.answer(
            LEXICON_RU["set_location"], reply_markup=set_location_kb()
        )
        await state.update_data(sex=callback.data)
        await state.set_state(FSMSettings.set_location)
    except:
        await state.clear()
        await callback.message.answer(ERROR_LEXICON_RU["InternalError"])


@user_router.message(F.location, StateFilter(FSMSettings.set_location))
async def profile_location(message: Message, state: FSMContext):
    """
    Set user location and send a message
    which allows the user to set his currency.
    """

    try:
        latitude = round(message.location.latitude, 3)
        longitude = round(message.location.longitude, 3)

        res = await convert_coordinates(
            latitude, longitude
        )

        if res:
            country, city = res[0], res[1]
            await message.answer(
                LEXICON_RU["set_currency"], reply_markup=set_currency_kb()
            )
            await state.update_data(
                latitude=latitude,
                longitude=longitude,
                country=country,
                city=city,
            )
            await state.set_state(FSMSettings.set_currency)
        else:
            await message.answer(ERROR_LEXICON_RU["GeocodingError"])

    except GeocodingError:
        await message.answer(ERROR_LEXICON_RU["GeocodingError"])
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@user_router.callback_query(StateFilter(FSMSettings.set_currency))
async def profile_currency(callback: CallbackQuery, state: FSMContext):
    """
    Set user currency and send a message
    which allows set his bio.
    """

    try:
        await callback.answer()
        await callback.message.answer(
            LEXICON_RU["set_bio"], reply_markup=leave_blank_kb()
        )
        await state.update_data(currency=callback.data)
        await state.set_state(FSMSettings.set_bio)
    except:
        await state.clear()
        await callback.message.answer(ERROR_LEXICON_RU["InternalError"])


@user_router.message(F.text, StateFilter(FSMSettings.set_bio))
async def profile_bio(
    message: Message,
    state: FSMContext,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Set user bio and send a message
    which allows see the menu.
    """

    try:
        if message.text != KB_LEXICON_RU["leave_blank"]:
            bio = message.text
        else:
            bio = ""

        data = await state.get_data()
        data["bio"] = bio
        await cache.delete(f"user-{data["id"]}")
        await create_update_user(data, sessionmaker)
        await message.answer(LEXICON_RU["settings_done"], reply_markup=menu_kb())
        await state.clear()

    except DatabaseError:
        await message.answer(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@user_router.callback_query(F.data == "edit_profile", StateFilter(default_state))
async def edit_profile(callback: CallbackQuery, state: FSMContext):
    """
    Let the user edit his profile.
    """

    try:
        await callback.answer()
        await callback.message.answer(
            LEXICON_RU["edit_profile"], reply_markup=leave_same_kb()
        )
        await state.update_data(
            id=callback.from_user.id, username=callback.from_user.username
        )
        await state.set_state(FSMSettings.edit_age)
    except:
        await state.clear()
        await callback.message.answer(ERROR_LEXICON_RU["InternalError"])


@user_router.message(F.text, StateFilter(FSMSettings.edit_age))
async def edit_age(message: Message, state: FSMContext):
    """
    Edit user age and send a message
    which allows the user to edit his location.
    """

    try:
        if message.text != KB_LEXICON_RU["leave_same"]:
            user_age = int(message.text)

            if user_age not in range(1, 121):
                await message.answer(ERROR_LEXICON_RU["incorrect_data"])
            else:
                await state.update_data(age=user_age)

        await message.answer(
            LEXICON_RU["edit_sex"],
            reply_markup=leave_same_kb(with_sex=True),
        )
        await state.set_state(FSMSettings.edit_sex)

    except ValueError:
        await message.answer(ERROR_LEXICON_RU["incorrect_data"])
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@user_router.message(F.text, StateFilter(FSMSettings.edit_sex))
async def edit_sex(message: Message, state: FSMContext):
    """
    Edit user sex and send a message
    which allows the user to edit his location.
    """

    try:
        if message.text != KB_LEXICON_RU["leave_same"]:
            await state.update_data(sex=message.text)

        await message.answer(
            LEXICON_RU["edit_location"],
            reply_markup=leave_same_kb(with_location=True),
        )
        await state.set_state(FSMSettings.edit_location)
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@user_router.message(F.text | F.location, StateFilter(FSMSettings.edit_location))
async def edit_location(message: Message, state: FSMContext):
    """
    Edit user location and send a message
    which allows the user to edit his bio.
    """

    try:
        if message.text != KB_LEXICON_RU["leave_same"]:
            latitude = round(message.location.latitude, 3)
            longitude = round(message.location.longitude, 3)

            res = await convert_coordinates(latitude, longitude)

            if res:
                country, city = res[0], res[1]
                await message.answer(
                    LEXICON_RU["edit_currency"],
                    reply_markup=leave_same_kb(with_currency=True),
                )
                await state.update_data(
                    latitude=latitude,
                    longitude=longitude,
                    country=country,
                    city=city,
                )
                await state.set_state(FSMSettings.edit_currency)
            else:
                await message.answer(ERROR_LEXICON_RU["GeocodingError"])
        else:
            await message.answer(
                LEXICON_RU["edit_currency"],
                reply_markup=leave_same_kb(with_currency=True),
            )
            await state.set_state(FSMSettings.edit_currency)

    except GeocodingError:
        await message.answer(ERROR_LEXICON_RU["GeocodingError"])
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@user_router.message(F.text, StateFilter(FSMSettings.edit_currency))
async def edit_currency(message: Message, state: FSMContext):
    """
    Edit user currency and send a message
    which allows edit his bio.
    """

    try:
        if (
            message.text != KB_LEXICON_RU["leave_same"]
            and message.text.split()[1] in CURRENCY_DICT
        ):
            await state.update_data(currency=message.text)

        await message.answer(
            LEXICON_RU["edit_bio"], reply_markup=leave_same_kb(with_blank=True)
        )
        await state.set_state(FSMSettings.edit_bio)
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@user_router.message(F.text, StateFilter(FSMSettings.edit_bio))
async def edit_bio(
    message: Message,
    state: FSMContext,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Edit user bio and send a message
    which allows see the menu.
    """

    try:
        data = await state.get_data()

        if message.text not in (
            KB_LEXICON_RU["leave_blank"],
            KB_LEXICON_RU["leave_same"],
        ):
            data["bio"] = message.text
        elif message.text == KB_LEXICON_RU["leave_blank"]:
            data["bio"] = ""

        user_id = data["id"]
        await cache.delete(f"user-{user_id}")
        await create_update_user(data, sessionmaker)
        data["id"] = user_id

        for k, v in user.items():
            if k not in data:
                data[k] = v

        await message.answer(
            LEXICON_RU["editing_done"] + "\n\n" + create_profile(data),
            reply_markup=edit_kb(),
        )
        await state.clear()

    except DatabaseError:
        await message.answer(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await message.answer(ERROR_LEXICON_RU["InternalError"])
