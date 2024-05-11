from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from lexicon import KB_LEXICON_RU
from database import get_items


async def paginator_kb(
    user: dict,
    page: int,
    source_type: str,
    sessionmaker: async_sessionmaker[AsyncSession],
    is_admin: bool = False,
    trip_id: int | None = None,
    expense_id: int | None = None,
) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to select a trip.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    types = {
        "trips": "trips-page-",
        "notes": f"notes-{trip_id}-page-",
        "friends": f"friends-{trip_id}-page-",
        "find_friends": f"found-friends-{trip_id}-page-",
        "locations": f"locations-{trip_id}-page-",
        "expenses": f"expenses-{trip_id}-page-",
        "expense_debtors": f"expense-debtors-{expense_id}-page-",
    }

    page_type = types[source_type]
    items, pages = await get_items(
        user, page * 5, source_type, sessionmaker, trip_id, expense_id
    )

    match source_type:
        case "trips":
            for trip, trip_id in items:
                kb_builder.row(
                    InlineKeyboardButton(
                        text=trip,
                        callback_data=f"trip-{trip_id}",
                    ),
                )

            if len(tuple(kb_builder.buttons)) == 0:
                kb_builder.row(
                    InlineKeyboardButton(
                        text=KB_LEXICON_RU["new_trip"],
                        callback_data="new_trip",
                    ),
                )
                return kb_builder.as_markup()

        case "notes":
            for note_name, note_id in items:
                kb_builder.row(
                    InlineKeyboardButton(
                        text=note_name,
                        callback_data=f"notes-{trip_id}-note-{note_id}",
                    ),
                )

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

        case "friends":
            for friend_username in items:
                kb_builder.row(
                    InlineKeyboardButton(
                        text=f"@{friend_username}",
                        callback_data="friends-"
                        + f"{trip_id}-friend-{friend_username}",
                    ),
                )

            if is_admin:
                kb_builder.row(
                    InlineKeyboardButton(
                        text=KB_LEXICON_RU["add_friend"],
                        callback_data=f"friends-{trip_id}-add-friend",
                    ),
                )
                kb_builder.row(
                    InlineKeyboardButton(
                        text=KB_LEXICON_RU["find_friends"],
                        callback_data=f"found-users-{trip_id}-page-0",
                    ),
                )
            kb_builder.row(
                InlineKeyboardButton(
                    text=KB_LEXICON_RU["back_to_trip"],
                    callback_data=f"trip-{trip_id}",
                ),
            )

        case "find_friends":
            for username in items:
                kb_builder.row(
                    InlineKeyboardButton(
                        text=f"@{username}",
                        callback_data=f"trip-{trip_id}-user-{username}",
                    ),
                )

            kb_builder.row(
                InlineKeyboardButton(
                    text=KB_LEXICON_RU["back_to_friends"],
                    callback_data=f"friends-{trip_id}-page-0",
                ),
            )

        case "locations":
            for country, city, latitude, longitude in items:
                latitude = str(latitude).replace("-", "*")
                longitude = str(longitude).replace("-", "*")

                kb_builder.row(
                    InlineKeyboardButton(
                        text=f"{country}, {city}",
                        callback_data="locations-"
                        + f"{trip_id}-location-{latitude}-{longitude}",
                    ),
                )

            kb_builder.row(
                InlineKeyboardButton(
                    text=KB_LEXICON_RU["route"],
                    callback_data=f"locations-{trip_id}-route",
                ),
            )

            if is_admin:
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

        case "expenses":
            for name, expense_id in items:
                kb_builder.row(
                    InlineKeyboardButton(
                        text=name,
                        callback_data=f"trip-{trip_id}-expense-{expense_id}-page-0",
                    ),
                )

            kb_builder.row(
                InlineKeyboardButton(
                    text=KB_LEXICON_RU["new_expense"],
                    callback_data=f"expenses-{trip_id}-new-expense",
                ),
            )
            kb_builder.row(
                InlineKeyboardButton(
                    text=KB_LEXICON_RU["back_to_trip"],
                    callback_data=f"trip-{trip_id}",
                ),
            )

        case "expense_debtors":
            for username in items:
                kb_builder.row(
                    InlineKeyboardButton(
                        text=f"@{username}",
                        callback_data=f"expense-{expense_id}-debtor-{username}",
                    ),
                )

            if is_admin:
                kb_builder.row(
                    InlineKeyboardButton(
                        text=KB_LEXICON_RU["new_expense_debtor"],
                        callback_data=f"expenses-{expense_id}-new-debtor",
                    ),
                )
                kb_builder.row(
                    InlineKeyboardButton(
                        text=KB_LEXICON_RU["expense_game"],
                        callback_data=f"trip-{trip_id}-expenses-{expense_id}-game",
                    ),
                )
                kb_builder.row(
                    InlineKeyboardButton(
                        text=KB_LEXICON_RU["edit"],
                        callback_data=f"edit-expenses-{expense_id}",
                    ),
                    InlineKeyboardButton(
                        text=KB_LEXICON_RU["delete"],
                        callback_data=f"pre-delete-expenses-{trip_id}-expense-{expense_id}",
                    ),
                )

            kb_builder.row(
                InlineKeyboardButton(
                    text=KB_LEXICON_RU["back_to_expenses"],
                    callback_data=f"expenses-{trip_id}-page-0",
                ),
            )

    if page != 0 and pages != 0:
        kb_builder.row(
            InlineKeyboardButton(
                text=f"\U00002B05 Страница {page}",
                callback_data=f"{page_type}{page - 1}",
            ),
            InlineKeyboardButton(
                text=f"\U000027A1 Страница {page + 2}",
                callback_data=f"{page_type}{page + 1}",
            ),
        )
    elif page != 0 and pages == 0:
        kb_builder.row(
            InlineKeyboardButton(
                text=f"\U00002B05 Страница {page}",
                callback_data=f"{page_type}{page - 1}",
            ),
        )
    elif page == 0 and pages != 0:
        kb_builder.row(
            InlineKeyboardButton(
                text=f"\U000027A1 Страница {page + 2}",
                callback_data=f"{page_type}{page + 1}",
            ),
        )
    return kb_builder.as_markup()
