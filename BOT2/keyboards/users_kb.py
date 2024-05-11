from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from lexicon import KB_LEXICON_RU, CURRENCY_DICT


def set_sex_kb() -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to set his sex.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["male"],
            callback_data=KB_LEXICON_RU["male"],
        ),
        InlineKeyboardButton(
            text=KB_LEXICON_RU["female"],
            callback_data=KB_LEXICON_RU["female"],
        ),
    )
    return kb_builder.as_markup()


def set_location_kb() -> ReplyKeyboardMarkup:
    """
    Build a keyboard which allows the user to set his location.
    """

    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    kb_builder.row(
        KeyboardButton(
            text=KB_LEXICON_RU["set_location"],
            request_location=True,
        ),
    )
    return kb_builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def set_currency_kb() -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to set currency.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=CURRENCY_DICT["RUB"],
            callback_data=CURRENCY_DICT["RUB"],
        ),
        InlineKeyboardButton(
            text=CURRENCY_DICT["USD"],
            callback_data=CURRENCY_DICT["USD"],
        ),
        InlineKeyboardButton(
            text=CURRENCY_DICT["EUR"],
            callback_data=CURRENCY_DICT["EUR"],
        ),
    )
    kb_builder.row(
        InlineKeyboardButton(
            text=CURRENCY_DICT["AED"],
            callback_data=CURRENCY_DICT["AED"],
        ),
        InlineKeyboardButton(
            text=CURRENCY_DICT["GBP"],
            callback_data=CURRENCY_DICT["GBP"],
        ),
        InlineKeyboardButton(
            text=CURRENCY_DICT["CNY"],
            callback_data=CURRENCY_DICT["CNY"],
        ),
    )
    kb_builder.row(
        InlineKeyboardButton(
            text=CURRENCY_DICT["TRY"],
            callback_data=CURRENCY_DICT["TRY"],
        ),
        InlineKeyboardButton(
            text=CURRENCY_DICT["EGP"],
            callback_data=CURRENCY_DICT["EGP"],
        ),
        InlineKeyboardButton(
            text=CURRENCY_DICT["INR"],
            callback_data=CURRENCY_DICT["INR"],
        ),
    )
    return kb_builder.as_markup()


def leave_blank_kb() -> ReplyKeyboardMarkup:
    """
    Build a keyboard which allows the user to leave the field blank.
    """

    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    kb_builder.row(KeyboardButton(text=KB_LEXICON_RU["leave_blank"]))
    return kb_builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def menu_kb() -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to see the menu.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["my_trips"],
            callback_data="trips-page-0",
        ),
    )
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["new_trip"],
            callback_data="new_trip",
        ),
    )
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["currency"],
            callback_data="currency",
        ),
    )
    return kb_builder.as_markup()


def edit_kb() -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to edit his profile.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["edit"],
            callback_data="edit_profile",
        ),
    )
    return kb_builder.as_markup()


def leave_same_kb(
    with_blank: bool = False,
    with_sex: bool = False,
    with_location: bool = False,
    with_currency: bool = False,
) -> ReplyKeyboardMarkup:
    """
    Build a keyboard which allows the to skip editing this field.
    """

    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

    if with_blank:
        kb_builder.row(
            KeyboardButton(text=KB_LEXICON_RU["leave_blank"]),
        )
    if with_location:
        kb_builder.row(
            KeyboardButton(
                text=KB_LEXICON_RU["set_location"],
                request_location=True,
            ),
        )
    if with_sex:
        kb_builder.row(
            KeyboardButton(
                text=KB_LEXICON_RU["male"],
            ),
            KeyboardButton(
                text=KB_LEXICON_RU["female"],
            ),
        )
    if with_currency:
        kb_builder.row(
            KeyboardButton(
                text=CURRENCY_DICT["RUB"],
            ),
            KeyboardButton(
                text=CURRENCY_DICT["USD"],
            ),
            KeyboardButton(
                text=CURRENCY_DICT["EUR"],
            ),
        )
        kb_builder.row(
            KeyboardButton(
                text=CURRENCY_DICT["AED"],
            ),
            KeyboardButton(
                text=CURRENCY_DICT["GBP"],
            ),
            KeyboardButton(
                text=CURRENCY_DICT["CNY"],
            ),
        )
        kb_builder.row(
            KeyboardButton(
                text=CURRENCY_DICT["TRY"],
            ),
            KeyboardButton(
                text=CURRENCY_DICT["EGP"],
            ),
            KeyboardButton(
                text=CURRENCY_DICT["INR"],
            ),
        )

    kb_builder.row(
        KeyboardButton(text=KB_LEXICON_RU["leave_same"]),
    )
    return kb_builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def my_trips_kb() -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to see his trips.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["my_trips"],
            callback_data="trips-page-0",
        ),
    )
    return kb_builder.as_markup()
