import json

from cashews import Cache
from aiohttp import ClientSession

from errors import ServiceConnectionError
from config_data import Config, load_config


config: Config = load_config()
cache: Cache = config.tg_bot.cache


@cache(ttl="30m")
async def convert_currency(
    amount: float,
    base_currency: str,
    convert_to: str,
) -> dict:
    """
    Convert amount of user currency.
    """

    url = "https://calcus.ru/calculate/Currency"
    data = {
        "currency1": base_currency.split()[1],
        "currency2": convert_to.split()[1],
        "value": amount,
    }

    try:
        async with ClientSession() as session:
            async with session.post(url, data=data) as response:
                converted = json.loads(await response.text())

        if amount == 1:
            pre_rate = converted.pop("one").split(" = ")
        else:
            pre_rate = converted.pop("one").split("<br>")[1].split(" = ")

        pre_rate_2 = pre_rate[1].split()
        rate_2 = round(float(pre_rate_2[0].replace(",", ".").replace(" ", "")), 2)
        rate = pre_rate[0] + " = " + str(rate_2).replace(".", ",") + " " + pre_rate_2[1]

        converted["base_currency"] = base_currency
        converted["convert_to"] = convert_to
        converted["rate"] = rate
        converted["input"] = str(
            round(float(converted["input"].replace(",", ".").replace(" ", "")), 2)
        ).replace(".", ",")
        converted["value"] = str(
            round(float(converted["value"].replace(",", ".").replace(" ", "")), 2)
        ).replace(".", ",")

        return converted

    except:
        raise ServiceConnectionError
