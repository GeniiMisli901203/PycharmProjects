import itertools
import json
import asyncio
import peewee
import aiohttp

from loader import bot, db, HEADERS, SORT_ORDER, get_hotel_data_from_json
from typing import Dict, Optional, Generator
from collections.abc import AsyncIterable


async def request_to_api(url: str, headers: Dict, querystring: Dict) -> Optional[str]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url,
                               headers=headers,
                               params=querystring,
                               timeout=10) as response:
            if response.status == 200:
                return await response.text()
            else:
                return None


async def get_destination_id(city: str, user_request: peewee.Model) -> bool:
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {
        "query": city,
        "locale": "ru_RU",
        "currency": "RUB"
    }

    response = await request_to_api(url,
                                    headers=HEADERS,
                                    querystring=querystring)
    try:
        response_dict = json.loads(response)
        suggestions = response_dict.get("suggestions")
        entities = suggestions[0].get("entities")
        destination_id = entities[0].get("destinationId")

        with db:
            user_request.destination_id = destination_id
            user_request.save()

        return True

    except (IndexError, AttributeError):
        return False


async def get_hotels_info(chat_id: int, user_request: peewee.Model) -> None:
    problem_msg = "Упс. Что-то пошло не так. Подождите минутку и попробуйте ещё раз"

    url = "https://hotels4.p.rapidapi.com/properties/list"
    sort_order = SORT_ORDER[user_request.command]

    querystring = {
        "destinationId": user_request.destination_id,
        "pageNumber": "1",
        "pageSize": str(user_request.hotels_count),
        "checkIn": str(user_request.check_in),
        "checkOut": str(user_request.check_out),
        "adults1": "1",
        "sortOrder": sort_order,
        "locale": "ru_RU",
        "currency": "RUB",
    }

    response = await request_to_api(url,
                                    headers=HEADERS,
                                    querystring=querystring)

    if response is not None:
        await send_final_result(chat_id, response, user_request)
    else:
        await bot.send_message(chat_id, problem_msg)


async def get_hotel_photos(hotel_id: str, count: int) -> AsyncIterable:
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": hotel_id}
    response = await request_to_api(url,
                                    headers=HEADERS,
                                    querystring=querystring)

    if response is not None:

        try:
            photos = json.loads(response).get("hotelImages")
        except (json.JSONDecodeError, AttributeError) as json_or_none_err:
            print(json_or_none_err)
            return

        count = count if len(photos) > count else len(photos)
        for i in range(count):
            yield photos[i]

    else:
        return


async def send_final_result(chat_id: int, full_response: str, user_request: peewee.Model) -> None:
    hotels = (hotel for hotel in get_hotel_data_from_json(full_response, user_request))
    with db:
        for _ in range(user_request.hotels_count):
            hotel = next(hotels)
            if hotel is None:
                continue
            if user_request.photos_count is not None:
                await send_hotel_photos(chat_id,
                                        hotel.hotel_id,
                                        user_request.photos_count)
            await send_hotel_info(chat_id, hotel)


async def send_hotel_info(chat_id: int, hotel: peewee.Model) -> None:
    cur_hotel_info = f"{hotel.name}\n" \
                     f"\u2605{hotel.rating}\n" \
                     f"Адрес: {hotel.address}\n" \
                     f"Расстояние до центра города: {hotel.distance_to_center}\n" \
                     f"Цена: {hotel.price}\n" \
                     f"{hotel.hotel_url}"

    await bot.send_message(chat_id, cur_hotel_info)


async def send_hotel_photos(chat_id: int, hotel_id: str, count: int) -> Optional[Generator]:
    problem_msg = "Не удалось получить фото объекта"
    try:
        print("getting to generate photos")
        # photos = tuple(photo async for photo in get_hotel_photos(hotel_id, count))
        size = 'y'
        coros = []
        async for photo in get_hotel_photos(hotel_id, count):
            coros.append(send_one_photo(chat_id, photo, size))
    except ValueError:
        await bot.send_message(chat_id, problem_msg)
        return None

    # size = 'y'
    print("photos list generated")
    # coros = tuple(send_one_photo(chat_id, photo, size) for photo in photos)

    try:
        return await asyncio.wait(coros, return_when=asyncio.ALL_COMPLETED)
    except Exception as ex:
        print(ex)
        await bot.send_message(chat_id, problem_msg)


async def send_one_photo(chat_id: int, photo_info: Dict, size: str) -> None:
    try:
        photo_url_raw: str = photo_info.get("baseUrl")
        photo_url = photo_url_raw.replace("{size}", size)
        await bot.send_photo(chat_id, photo_url)
    except Exception as ex:
        print(ex)
