from __future__ import annotations

import json
import os

import peewee
import tb
import telebot.types as tt
import datetime

from dotenv import load_dotenv

from api_requests import get_destination_id, get_hotels_info
from loader import bot, db, UserRequest
from abc import ABC, abstractmethod
from typing import Union, Iterable

load_dotenv()

TOKEN = os.getenv("7056995214:AAGhdLzym_AalGRB-3PZ0ZpTEWTTy1DLGys")
RAPIDAPI_KEY = os.getenv("")

HEADERS = {
    "x-rapidapi-host": "hotels4.p.rapidapi.com",
    f"x-rapidapi-key": RAPIDAPI_KEY
}

SORT_ORDER = {
    "/lowprice": "PRICE",
    "/highprice": "PRICE_HIGHEST_FIRST",
    "/bestdeal": "DISTANCE_FROM_LANDMARK"
}

bot = tb.AsyncTeleBot(TOKEN)
db = peewee.SqliteDatabase("hotels.sqlite")
user_contexts: dict = {}


class UserRequest(peewee.Model):
    user_id = peewee.IntegerField()
    command = peewee.CharField()
    request_dt = peewee.DateTimeField()
    check_in = peewee.DateField()
    check_out = peewee.DateField()
    city = peewee.CharField(null=True)
    destination_id = peewee.CharField(null=True)
    hotels_count = peewee.IntegerField(null=True)
    photos_count = peewee.IntegerField(null=True)
    price_min = peewee.IntegerField(null=True)
    price_max = peewee.IntegerField(null=True)
    dictance_to_center_min = peewee.IntegerField(null=True)
    dictance_to_center_max = peewee.IntegerField(null=True)

    class Meta:
        database = db


class HotelData(peewee.Model):
    request_id = peewee.ForeignKeyField(UserRequest,
                                        verbose_name="request")
    hotel_id = peewee.CharField()
    name = peewee.CharField()
    rating = peewee.CharField()
    address = peewee.CharField(null=True)
    distance_to_center = peewee.CharField(null=True)
    price = peewee.CharField()
    hotel_url = peewee.CharField()

    class Meta:
        database = db


class PhotoUrl(peewee.Model):
    hotel = peewee.ForeignKeyField(HotelData,
                                   verbose_name="hotel")
    photo_url = peewee.CharField()

    class Meta:
        database = db


def get_hotel_data_from_json(full_data: str, user_request: peewee.Model) -> Iterable:
    response_dict = json.loads(full_data)
    data = response_dict.get("data")
    body = data.get("body")
    search_results = body.get("searchResults")
    results = search_results.get("results")
    counter = 0

    for hotel in results:

        if counter >= user_request.hotels_count:
            raise StopIteration

        try:
            hotel_id = hotel.get("id")
            name = hotel.get("name")
            star_rating = hotel.get("starRating")
            address = hotel.get("address").get("streetAddress")
            landmarks = hotel.get("landmarks")
            distance_to_center = None
            price = hotel.get("ratePlan").get("price").get("current")
            url = f"https://ru.hotels.com/ho{hotel_id}/?q-check-in={user_request.check_in}" \
                  f"&q-check-out={user_request.check_out}&q-rooms=1&q-room-0-adults=1&q-room-0-children=0"

            for landmark in landmarks:
                label = landmark.get("label").lower()
                if "центр" in label or "center" in label:
                    distance_to_center = landmark.get("distance")
        except AttributeError:
            yield None
            continue

        with db:
            new_hotel_data = HotelData.create(
                request_id=user_request.get_id(),
                hotel_id=hotel_id,
                name=name,
                rating=star_rating,
                address=address,
                distance_to_center=distance_to_center,
                price=price,
                hotel_url=url
            )

        counter += 1
        yield new_hotel_data


with db:
    if not UserRequest.table_exists():
        UserRequest.create_table()

    if not HotelData.table_exists():
        HotelData.create_table()

    if not PhotoUrl.table_exists():
        PhotoUrl.create_table()
