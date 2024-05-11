from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon import KB_LEXICON_RU


def base_locations_kb(trip_id: int) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to add another
    location or open the trip info.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["new_location"],
            callback_data=f"locations-{trip_id}-new-location",
        ),
    )
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_trip"],
            callback_data=f"trip-{trip_id}",
        ),
    )
    return kb_builder.as_markup()


def base_location_kb(
    trip_id: int,
    latitude: float,
    longitude: float,
    is_admin: bool,
) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to delete the location
    or go back to the notes.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    latitude = str(latitude).replace("-", "*")
    longitude = str(longitude).replace("-", "*")

    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["weather"],
            callback_data=f"locations-{trip_id}-location-"
            + f"{latitude}-{longitude}-weather",
        ),
    )
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["landmarks"],
            callback_data=f"locations-{trip_id}-location-"
            + f"{latitude}-{longitude}-landmarks",
        ),
    )

    if is_admin:
        kb_builder.row(
            InlineKeyboardButton(
                text=KB_LEXICON_RU["delete"],
                callback_data="pre-delete-locations-"
                + f"{trip_id}-location-{latitude}-{longitude}",
            ),
        )

    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_locations"],
            callback_data=f"locations-{trip_id}-page-0",
        ),
    )
    return kb_builder.as_markup()


def confirm_location_deletion_kb(
    trip_id: int,
    latitude: float,
    longitude: float,
) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user
    to finally remove the location from the trip.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    latitude = str(latitude).replace("-", "*")
    longitude = str(longitude).replace("-", "*")
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["delete"],
            callback_data="finally-remove-locations-"
            + f"{trip_id}-location-{latitude}-{longitude}",
        ),
        InlineKeyboardButton(
            text=KB_LEXICON_RU["cancel_deletion"],
            callback_data=f"cancel-locations-{trip_id}-deletion",
        ),
    )
    return kb_builder.as_markup()


def back_to_locations_kb(trip_id: int) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to go back to the locations.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_locations"],
            callback_data=f"locations-{trip_id}-page-0",
        ),
    )
    return kb_builder.as_markup()


def back_to_location_kb(
    trip_id: int,
    latitude: float,
    longitude: float,
) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to go back to the location.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_location"],
            callback_data=f"locations-{trip_id}-location-{latitude}-{longitude}",
        ),
    )
    return kb_builder.as_markup()
