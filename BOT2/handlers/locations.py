import asyncio
from datetime import datetime as dt, date

import aiofiles.os as aos
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, FSInputFile
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from states import FSMLocation
from services import create_location_info
from config_data import Config, load_config
from external_services import convert_coordinates
from lexicon import LEXICON_RU, ERROR_LEXICON_RU
from errors import (
    DatabaseError,
    GeocodingError,
    InvalidDateError,
    LocationExistsError,
    IsStartPointError,
)
from database import (
    get_trip_db,
    add_location_db,
    get_location_db,
    delete_location_db,
)
from keyboards import (
    paginator_kb,
    base_location_kb,
    base_locations_kb,
    confirm_location_deletion_kb,
    back_to_locations_kb,
)


location_router: Router = Router()
config: Config = load_config()
semaphore: asyncio.BoundedSemaphore = config.tg_bot.semaphore


@location_router.callback_query(
    F.data.func(lambda x: "locations-" in x and "-page-" in x),
    StateFilter(default_state),
)
async def locations(
    callback: CallbackQuery,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Send trip locations.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        trip_id = int(data[1])
        trip = await get_trip_db(trip_id, sessionmaker)
        await callback.message.answer(
            LEXICON_RU["locations"],
            reply_markup=(
                await paginator_kb(
                    user,
                    int(data[-1]),
                    "locations",
                    sessionmaker,
                    user["username"] == trip["username"],
                    trip_id,
                )
            ),
        )
    except:
        await callback.message.answer(ERROR_LEXICON_RU["InternalError"])


@location_router.callback_query(
    F.data.func(lambda x: "-new-location" in x),
    StateFilter(default_state),
)
async def new_location(callback: CallbackQuery, state: FSMContext):
    """
    Let the user add a new loction to the trip.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        await callback.message.edit_text(LEXICON_RU["new_location"])
        await state.update_data(trip_id=int(data[1]))
        await state.set_state(FSMLocation.add_geo)
    except:
        await state.clear()
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@location_router.message(
    F.location,
    StateFilter(FSMLocation.add_geo),
)
async def location_geo(message: Message, user: dict, state: FSMContext):
    """
    Set new location and let the user select the dates.
    """

    try:
        latitude = round(message.location.latitude, 3)
        longitude = round(message.location.longitude, 3)

        if user["latitude"] == latitude and user["longitude"] == longitude:
            raise IsStartPointError

        res = await convert_coordinates(latitude, longitude)

        if res:
            country, city = res[0], res[1]
            await message.answer(LEXICON_RU["location_dates"])
            await state.update_data(
                country=country,
                city=city,
                latitude=latitude,
                longitude=longitude,
            )
            await state.set_state(FSMLocation.set_location_dates)
        else:
            await message.answer(ERROR_LEXICON_RU["GeocodingError"])

    except IsStartPointError:
        await message.answer(ERROR_LEXICON_RU["IsStartPointError"])
    except GeocodingError:
        await message.answer(ERROR_LEXICON_RU["GeocodingError"])
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@location_router.message(F.text, StateFilter(FSMLocation.set_location_dates))
async def location_dates(
    message: Message, state: FSMContext, sessionmaker: async_sessionmaker[AsyncSession]
):
    """
    Set location dates and send buttons (add another, trip).
    """

    try:
        d1, d2 = map(
            lambda date: dt.strptime(date, "%d.%m.%Y"), message.text.split("-")
        )

        if date(d1.year, d1.month, d1.day) >= date.today() and d2 > d1:
            data = await state.get_data()
            trip_id = data["trip_id"]
            data["start_date"] = d1
            data["end_date"] = d2
            await add_location_db(data, sessionmaker)
            await message.answer(
                LEXICON_RU["location_addded"],
                reply_markup=base_locations_kb(trip_id),
            )

            route_photo = FSInputFile(f"./files/routes/route-{trip_id}.jpeg")

            # delete the old route photo because of new location in the trip
            async with semaphore:
                if await aos.path.isfile(route_photo.path):
                    await aos.remove(route_photo.path)

            await state.clear()
        else:
            await message.answer(ERROR_LEXICON_RU["incorrect_data"])

    except InvalidDateError:
        await message.answer(
            ERROR_LEXICON_RU["InvalidDateError"],
            reply_markup=base_locations_kb(trip_id),
        )
    except LocationExistsError:
        await state.clear()
        await message.answer(
            ERROR_LEXICON_RU["LocationExistsError"],
            reply_markup=base_locations_kb(trip_id),
        )
    except DatabaseError:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await message.answer(ERROR_LEXICON_RU["incorrect_data"])


@location_router.callback_query(
    F.data.func(
        lambda x: "-location-" in x and "locations-" in x and x.count("-") == 4
    ),
    StateFilter(default_state),
)
async def get_location(
    callback: CallbackQuery,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Send the loction info with different buttons.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        trip_id = int(data[1])
        location_latitude = float(data[-2].replace("*", "-"))
        location_longitude = float(data[-1].replace("*", "-"))
        trip = await get_trip_db(trip_id, sessionmaker)
        location = await get_location_db(
            trip_id,
            location_latitude,
            location_longitude,
            sessionmaker,
        )
        await callback.message.edit_text(
            create_location_info(location),
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


@location_router.callback_query(
    F.data.func(lambda x: "pre-delete-locations-" in x), StateFilter(default_state)
)
async def pre_delete_location(callback: CallbackQuery):
    """
    Let the user delete the location.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        trip_id = int(data[3])
        location_latitude = float(data[-2].replace("*", "-"))
        location_longitude = float(data[-1].replace("*", "-"))
        await callback.message.edit_text(
            LEXICON_RU["confirm_deletion"],
            reply_markup=confirm_location_deletion_kb(
                trip_id,
                location_latitude,
                location_longitude,
            ),
        )
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@location_router.callback_query(
    F.data.func(lambda x: "finally-remove-locations-" in x), StateFilter(default_state)
)
async def finally_delete_location(
    callback: CallbackQuery,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    try:
        await callback.answer()
        data = callback.data.split("-")
        trip_id = int(data[3])
        location_latitude = float(data[-2].replace("*", "-"))
        location_longitude = float(data[-1].replace("*", "-"))
        await delete_location_db(
            trip_id,
            location_latitude,
            location_longitude,
            sessionmaker,
        )
        await callback.message.edit_text(
            LEXICON_RU["deletion_done"],
            reply_markup=back_to_locations_kb(trip_id),
        )

        route_photo = FSInputFile(f"./files/routes/route-{trip_id}.jpeg")

        # delete the old route photo because of location deletion in the trip
        async with semaphore:
            if await aos.path.isfile(route_photo.path):
                await aos.remove(route_photo.path)

    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@location_router.callback_query(
    F.data.func(lambda x: "cancel-locations-" in x),
    StateFilter(default_state),
)
async def cancel_location_deletion(callback: CallbackQuery):
    try:
        await callback.answer()
        data = callback.data.split("-")
        await callback.message.edit_text(
            LEXICON_RU["deletion_canceled"],
            reply_markup=back_to_locations_kb(int(data[2])),
        )
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])
