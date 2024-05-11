from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon import KB_LEXICON_RU


def base_friends_kb(trip_id: int) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to add another
    friend or open the trip info.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["add_friend"],
            callback_data=f"friends-{trip_id}-add-friend",
        ),
    )
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_trip"], callback_data=f"trip-{trip_id}"
        ),
    )
    return kb_builder.as_markup()


def base_friend_kb(
    trip_id: int,
    friend_username: str,
    is_admin: bool,
) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to remove
    the friend from the trip or go back to the friend list.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    if is_admin:
        kb_builder.row(
            InlineKeyboardButton(
                text=KB_LEXICON_RU["delete"],
                callback_data="pre-delete-friends-"
                + f"{trip_id}-friend-{friend_username}",
            ),
        )

    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_friends"],
            callback_data=f"friends-{trip_id}-page-0",
        ),
    )
    return kb_builder.as_markup()


def confirm_friend_deletion_kb(
    trip_id: int, friend_username: str
) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user
    to finally remove the friend from the trip.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["delete"],
            callback_data="finally-remove-friends-"
            + f"{trip_id}-friend-{friend_username}",
        ),
        InlineKeyboardButton(
            text=KB_LEXICON_RU["cancel_deletion"],
            callback_data=f"cancel-friends-{trip_id}-deletion",
        ),
    )
    return kb_builder.as_markup()


def back_to_friends_kb(trip_id: int) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to go back to the friends section.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_friends"],
            callback_data=f"friends-{trip_id}-page-0",
        ),
    )
    return kb_builder.as_markup()


def base_found_user_kb(
    trip_id: int,
    found_user_username: str,
    is_admin: bool,
) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to add the
    found user to the trip or go back to the friend list.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    if is_admin:
        kb_builder.row(
            InlineKeyboardButton(
                text=KB_LEXICON_RU["add_user"],
                callback_data="friends-"
                + f"{trip_id}-invite-user-{found_user_username}",
            ),
        )

    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_found_users"],
            callback_data=f"found-users-{trip_id}-page-0",
        ),
    )
    return kb_builder.as_markup()


def back_found_users_kb(trip_id: int) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user go back
    to the found users list.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_found_users"],
            callback_data=f"found-users-{trip_id}-page-0",
        ),
    )
    return kb_builder.as_markup()
