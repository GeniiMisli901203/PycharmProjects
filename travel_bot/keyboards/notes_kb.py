from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon import KB_LEXICON_RU


def private_kb() -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to select
    if the new note is private.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["private_note"],
            callback_data="private_note",
        ),
        InlineKeyboardButton(
            text=KB_LEXICON_RU["unprivate_note"],
            callback_data="unprivate_note",
        ),
    )
    return kb_builder.as_markup()


def base_notes_kb(trip_id: int) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to upload another
    file or open the trip info.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["new_note"],
            callback_data=f"notes-{trip_id}-new-note",
        ),
    )
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_trip"],
            callback_data=f"trip-{trip_id}",
        ),
    )
    return kb_builder.as_markup()


def base_note_kb(trip_id: int, note_id: int, is_admin: bool) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to delete the trip
    or go back to the notes.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    if is_admin:
        kb_builder.row(
            InlineKeyboardButton(
                text=KB_LEXICON_RU["delete"],
                callback_data=f"pre-delete-notes-{trip_id}-note-{note_id}",
            ),
        )

    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_notes"],
            callback_data=f"notes-{trip_id}-page-0",
        ),
    )
    return kb_builder.as_markup()


def back_to_notes_kb(trip_id: int) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to go back to the notes.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_notes"],
            callback_data=f"notes-{trip_id}-page-0",
        ),
    )
    return kb_builder.as_markup()


def confirm_note_deletion_kb(trip_id: int, note_id: int) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to finally delete the trip.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["delete"],
            callback_data=f"finally-delete-notes-{trip_id}-note-{note_id}",
        ),
        InlineKeyboardButton(
            text=KB_LEXICON_RU["cancel_deletion"],
            callback_data=f"cancel-notes-{trip_id}-deletion",
        ),
    )
    return kb_builder.as_markup()
