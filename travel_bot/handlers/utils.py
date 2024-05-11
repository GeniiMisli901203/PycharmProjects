import asyncio
from datetime import datetime as dt

import aiofiles.os as aos
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, FSInputFile
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from states import FSMCurrency
from services import create_currency_info
from config_data import Config, load_config
from database import get_trip_db, get_location_db
from lexicon import LEXICON_RU, ERROR_LEXICON_RU, CURRENCY_DICT
from external_services import (
    get_route_photo,
    get_weather_forecast,
    convert_currency,
    get_sights_list,
)
from keyboards import (
    base_location_kb,
    back_to_location_kb,
    back_to_locations_kb,
    set_currency_kb,
)
from errors import (
    DatabaseError,
    NavigationError,
    NoLocationsError,
    WeatherDateError,
    ServiceConnectionError,
)


utils_router: Router = Router()
config: Config = load_config()
semaphore: asyncio.BoundedSemaphore = config.tg_bot.semaphore


@utils_router.callback_query(
    F.data.func(lambda x: "-route" in x),
    StateFilter(default_state),
)
async def route(
    callback: CallbackQuery,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Send the route photo.
    """

    try:
        await callback.answer()
        event = asyncio.Event()
        data = callback.data.split("-")
        trip_id = int(data[1])
        route_photo = FSInputFile(f"./files/routes/route-{trip_id}.jpeg")
        trip = await get_trip_db(trip_id, sessionmaker)
        wait = False

        if not await aos.path.isfile(route_photo.path):
            wait = True
            await callback.message.edit_text(LEXICON_RU["wait"])
            await asyncio.to_thread(
                get_route_photo,
                trip_id,
                user["latitude"],
                user["longitude"],
                trip["locations"],
                event,
            )
        else:
            event.set()

        await event.wait()

        if wait:
            await callback.message.delete()

        await callback.message.answer_photo(
            route_photo,
            LEXICON_RU["route"],
            reply_markup=back_to_locations_kb(trip_id),
        )

    except NavigationError:
        await callback.message.edit_text(
            ERROR_LEXICON_RU["NavigationError"],
            reply_markup=back_to_locations_kb(trip_id),
        )
    except NoLocationsError:
        await callback.message.edit_text(
            ERROR_LEXICON_RU["NoLocationsError"],
            reply_markup=back_to_locations_kb(trip_id),
        )
    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@utils_router.callback_query(
    F.data.func(lambda x: "-weather" in x),
    StateFilter(default_state),
)
async def weather(
    callback: CallbackQuery,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Send the location weather forecast for 16 days.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        trip_id = int(data[1])
        location_latitude = float(data[-3].replace("*", "-"))
        location_longitude = float(data[-2].replace("*", "-"))
        location = await get_location_db(
            trip_id,
            location_latitude,
            location_longitude,
            sessionmaker,
        )
        forecast = await get_weather_forecast(
            dt.strptime(location["start_date"], "%d.%m.%Y"),
            dt.strptime(location["end_date"], "%d.%m.%Y"),
            location_latitude,
            location_longitude,
        )

        await callback.message.edit_text(
            forecast + LEXICON_RU["weather_limitations"],
            reply_markup=back_to_location_kb(
                trip_id,
                location_latitude,
                location_longitude,
            ),
        )

    except WeatherDateError:
        await callback.message.edit_text(
            ERROR_LEXICON_RU["WeatherDateError"],
            reply_markup=back_to_location_kb(
                trip_id,
                location_latitude,
                location_longitude,
            ),
        )
    except ServiceConnectionError:
        await callback.message.edit_text(
            ERROR_LEXICON_RU["ServiceConnectionError"],
            reply_markup=back_to_location_kb(
                trip_id,
                location_latitude,
                location_longitude,
            ),
        )
    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@utils_router.callback_query(
    F.data.func(lambda x: "-landmarks" in x),
    StateFilter(default_state),
)
async def landmarks(
    callback: CallbackQuery,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Send the top 5 sights nearby.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        trip_id = int(data[1])
        trip = await get_trip_db(trip_id, sessionmaker)
        location_latitude = float(data[-3].replace("*", "-"))
        location_longitude = float(data[-2].replace("*", "-"))
        sights = await get_sights_list(
            location_latitude,
            location_longitude,
        )

        await callback.message.edit_text(
            sights + LEXICON_RU["landmarks_limitations"],
            reply_markup=back_to_location_kb(
                trip_id,
                location_latitude,
                location_longitude,
            ),
        )

    except ServiceConnectionError:
        await callback.message.edit_text(
            ERROR_LEXICON_RU["ServiceConnectionError"],
            reply_markup=base_location_kb(
                trip_id,
                location_latitude,
                location_longitude,
                user["username"] == trip["username"],
            ),
        )
    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@utils_router.callback_query(
    F.data == "currency",
    StateFilter(default_state),
)
async def convert_user_currency(
    callback: CallbackQuery,
    state: FSMContext,
):
    """
    Let the user choose the conversion currency.
    """

    try:
        await callback.answer()
        await callback.message.edit_text(
            LEXICON_RU["select_currency"], reply_markup=set_currency_kb()
        )
        await state.set_state(FSMCurrency.select_currency)
    except:
        await state.clear()
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@utils_router.callback_query(
    F.data.func(lambda x: x.split()[-1] in CURRENCY_DICT),
    StateFilter(FSMCurrency.select_currency),
)
async def conversion_currency(callback: CallbackQuery, user: dict, state: FSMContext):
    """
    Let the user enter the currency amount.
    """

    try:
        await callback.answer()
        await callback.message.edit_text(LEXICON_RU["enter_amount"])
        await state.update_data(
            base_currency=user["currency"], convert_to=callback.data
        )
        await state.set_state(FSMCurrency.set_amount)
    except:
        await state.clear()
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@utils_router.message(
    F.text,
    StateFilter(FSMCurrency.set_amount),
)
async def enter_currency_amount(message: Message, state: FSMContext):
    """
    Let the user convert currency.
    """

    try:
        amount = float(message.text.replace(",", "."))
        data = await state.get_data()
        data["amount"] = amount
        converted = await convert_currency(**data)
        await message.answer(create_currency_info(converted))
        await state.clear()

    except ServiceConnectionError:
        await message.answer(ERROR_LEXICON_RU["ServiceConnectionError"])
    except:
        await message.answer(ERROR_LEXICON_RU["incorrect_data"])


@utils_router.message()
async def unknown(message: Message):
    """
    Send a message that the bot can not understand the user.
    """

    await message.answer(LEXICON_RU["unknown"])
