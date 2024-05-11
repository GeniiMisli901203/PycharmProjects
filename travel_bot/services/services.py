from external_services import convert_currency


def create_profile(data: dict) -> str:
    """
    Create user profile from his data.
    """

    res = ""

    res += f"Telegram \U0001F194: {data["id"]}\n\n"
    res += f"\U0001F464 Имя пользователя: @{data["username"]}\n\n"
    emoji, sex = data["sex"].split()
    res += f"{emoji} Пол: {sex}\n\n"
    res += f"\U0001F4C5 Возраст: {data["age"]}\n\n"

    if data["city"]:
        res += f"\U0001F4CD Страна: {data["country"]}, город: {data["city"]}\n\n"
    else:
        res += f"\U0001F4CD Страна: {data["country"]}\n\n"

    res += f"\U0001F4B0 Валюта: {data["currency"]}\n\n"
    res += f"\U0001F4CB О себе: {data["bio"] if data["bio"] else " "}"

    return res


def create_trip_info(data: dict) -> str:
    """
    Create trip info table from its data.
    """

    res = ""

    res += f"\U0001F194: {data["id"]}\n\n"
    res += f"\U0001F464 Организатор: @{data["username"]}\n\n"
    res += f"\U0001F3F7	Название путешествия: {data["name"]}\n\n"
    res += f"\U0001F4CB	Краткое описание: {data["description"]}"

    return res


def create_location_info(data: dict) -> str:
    """
    Create location info table from its data.
    """

    res = ""

    res += f"\U0001F4CD Страна: {data["country"]}, город: {data["city"]}\n\n"
    res += f"\U0001F4C5 Даты: {data["start_date"]}-{data["end_date"]}"

    return res


def create_currency_info(data: dict) -> str:
    """
    Create currency conversion info table from its data.
    """

    res = ""

    res += f"\U0001F4B0 Результат конвертации {data["base_currency"]} \U00002192 {data["convert_to"]}\n\n"
    res += f"\U0001F4C8 Курс: {data["rate"]}\n\n"
    res += f"{data["input"]} {data["currency1"]} = {data["value"]} {data["currency2"]}"

    return res


def create_expense_info(data: dict) -> str:
    """
    Create expense info table from its data.
    """

    res = ""

    res += f"\U0001F194: {data["id"]}\n\n"
    res += f"\U0001F3F7 Название траты: {data["name"]}\n\n"
    res += f"\U0001F464 Кому должны: @{data["username"]}\n\n"
    res += f"\U0001F4C5 Дата: {data["date"].strftime("%d.%m.%Y")}\n\n"
    res += f"\U0001F9FE Общая сумма долга: {str(data["cost"]).replace(".", ",")} {data["currency"]}\n\n"
    res += "\U0001F465 Должники:"

    return res


async def create_debtor_info(debtor_data: dict, expense_data: dict) -> str:
    """
    Create debtor info table from his data.
    """

    res = ""

    res += create_profile(debtor_data) + "\n\n"
    cost = round(expense_data["cost"] / len(expense_data["debtors"]), 2)

    if debtor_data["currency"] != expense_data["currency"]:
        converted = await convert_currency(cost, expense_data["currency"], debtor_data["currency"])
        res += f"\U0001F9FE Cумма долга: {converted["value"]} {debtor_data["currency"]}\n\n"
    else:
        res += f"\U0001F9FE Cумма долга: {cost} {expense_data["currency"]}\n\n"

    return res


def invite_message(sender_username: str, trip_name: str) -> str:
    """
    Create a invite message from the trip data.
    """

    res = f"""
    \U0000263A Пользователь @{sender_username} пригласил вас в совместное путешествие "{trip_name}"
    """

    return res


def debtor_message(sender_username: str, trip_name: str, expense_name: str) -> str:
    """
    Create a debt message from the trip data.
    """

    res = f"""
    \U0000263A Пользователь @{sender_username} оплатил покупку.\
    \n\nСумму своего долга и более подробную информация вы можете найти в разделе "{trip_name}" \U00002192 "Траты" \U00002192 "{expense_name}"
    """

    return res
