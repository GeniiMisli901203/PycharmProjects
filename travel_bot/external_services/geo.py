import asyncio

from cashews import Cache
import plotly.io as pio
import plotly.graph_objects as go
from aiohttp import ClientSession
from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter
from openrouteservice import convert
from openrouteservice.directions import directions

from config_data import Config, load_config
from errors import (
    GeocodingError,
    NavigationError,
    NoLocationsError,
    ServiceConnectionError,
)


config: Config = load_config()
cache: Cache = config.tg_bot.cache


@cache(ttl="1h")
async def convert_coordinates(
    latitude: float,
    longitude: float,
) -> tuple[str | None, str | None] | None:
    """
    Get country and place from coordinates.
    """

    coordinates = f"{latitude}, {longitude}"

    try:
        async with Nominatim(
            user_agent="travel_bot", adapter_factory=AioHTTPAdapter
        ) as geolocator:
            res = await geolocator.reverse(coordinates, language="ru")

            if res:
                data = res.raw["address"]
                country = data.get("country", "")
                city = data.get("city", "")
                town = data.get("town", "")

                if not city and town:
                    place = town
                elif city and not town:
                    place = city
                else:
                    place = coordinates

                return country, place
            else:
                raise GeocodingError
    except:
        raise GeocodingError


def get_route_photo(
    trip_id: int,
    user_latitude: float,
    user_longitude: float,
    locations: list,
    event: asyncio.Event,
) -> None:
    """
    Create a pic with trip route.
    """

    if not locations:
        raise NoLocationsError

    client = config.tg_bot.openrouteservice
    coords = [(user_longitude, user_latitude)]

    for location in locations:
        coords.append((location["longitude"], location["latitude"]))

    try:
        routes = directions(client, coords)
        geometry = routes["routes"][0]["geometry"]
        distance = routes["routes"][0]["summary"]["distance"]
        coordinates = convert.decode_polyline(geometry)["coordinates"]

        latitudes = []
        longitudes = []

        for point in coordinates:
            latitudes.append(point[1])
            longitudes.append(point[0])

        fig = go.Figure(
            go.Scattermapbox(
                mode="markers+lines",
                lon=longitudes,
                lat=latitudes,
            )
        )

        zoom = 2

        if distance <= 7500:
            zoom = 11
        elif distance <= 15000:
            zoom = 10
        elif distance <= 35000:
            zoom = 9
        elif distance <= 40000:
            zoom = 8
        elif distance <= 500000:
            zoom = 7
        elif distance <= 700000:
            zoom = 6
        elif distance <= 800000:
            zoom = 5
        elif distance <= 1500000:
            zoom = 4
        elif distance <= 3000000:
            zoom = 3

        fig.update_layout(
            margin={"l": 0, "t": 0, "b": 0, "r": 0},
            mapbox={
                "center": {
                    "lon": longitudes[len(longitudes) // 2],
                    "lat": latitudes[len(latitudes) // 2],
                },
                "style": "open-street-map",
                "zoom": zoom,
            },
        )

        pio.write_image(fig, f"./files/routes/route-{trip_id}.jpeg", format="jpeg")
        event.set()

    except:
        raise NavigationError


@cache(ttl="12h")
async def get_sights_list(
    location_latitude: float,
    location_longitude: float,
) -> str:
    """
    Create a top 10 list of sights.
    """

    url = "https://api.geoapify.com/v2/places"
    key = config.tg_bot.geoapify
    params = {
        "fiter": f"circle:{location_longitude},{location_latitude},7500",
        "bias": f"proximity:{location_longitude},{location_latitude}",
        "categories": ",".join(
            (
                "national_park",
                "entertainment.museum",
                "entertainment.culture",
                "entertainment.zoo",
                "entertainment.planetarium",
            )
        ),
        "limit": 10,
        "lang": "ru",
        "apiKey": key,
    }
    res = "\U0001F51D 10 достопримечательностей рядом:\n\n"

    try:
        async with ClientSession() as session:
            async with session.get(url, params=params) as response:
                sights = (await response.json())["features"]

        for sight in sights:
            pre_res = ""
            pre_res += f"\U0001F3F7 Название: {sight['properties']['name']}\n"
            pre_res += f"\U0001F4CD Адрес: {sight['properties']['address_line2']}\n\n"
            res += pre_res

    except:
        raise ServiceConnectionError

    return res
