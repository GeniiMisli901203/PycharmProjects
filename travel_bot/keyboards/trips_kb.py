from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon import KB_LEXICON_RU


def trip_options_kb(trip_id: int, is_admin: bool) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to configure the trip.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["friends"],
            callback_data=f"friends-{trip_id}-page-0",
        ),
        InlineKeyboardButton(
            text=KB_LEXICON_RU["locations"],
            callback_data=f"locations-{trip_id}-page-0",
        ),
    )
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["notes"],
            callback_data=f"notes-{trip_id}-page-0",
        ),
        InlineKeyboardButton(
            text=KB_LEXICON_RU["expenses"],
            callback_data=f"expenses-{trip_id}-page-0",
        ),
    )

    if is_admin:
        kb_builder.row(
            InlineKeyboardButton(
                text=KB_LEXICON_RU["edit"],
                callback_data=f"edit-trip-{trip_id}",
            ),
            InlineKeyboardButton(
                text=KB_LEXICON_RU["delete"],
                callback_data=f"pre-delete-trip-{trip_id}",
            ),
        )
    return kb_builder.as_markup()


def confirm_trip_deletion_kb(trip_id: int) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to finally delete the trip.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["delete"],
            callback_data=f"finally-delete-trip-{trip_id}",
        ),
        InlineKeyboardButton(
            text=KB_LEXICON_RU["cancel_deletion"],
            callback_data="cancel-trip-deletion",
        ),
    )
    return kb_builder.as_markup()


def back_to_trip_kb(trip_id: int) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to go back to the trip.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_trip"],
            callback_data=f"trip-{trip_id}",
        ),
    )
    return kb_builder.as_markup()
