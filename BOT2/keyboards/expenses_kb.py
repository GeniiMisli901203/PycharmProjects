from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon import KB_LEXICON_RU


def base_expenses_kb(trip_id: int) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to add
    a new expense or open the trip info.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["new_expense"],
            callback_data=f"expenses-{trip_id}-new-expense",
        ),
    )
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_trip"], callback_data=f"trip-{trip_id}"
        ),
    )
    return kb_builder.as_markup()


def confirm_expense_deletion_kb(trip_id: int, expense_id: int) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user
    to finally delete the expense from the trip.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["delete"],
            callback_data=f"finally-remove-expense-{expense_id}-trip-{trip_id}",
        ),
        InlineKeyboardButton(
            text=KB_LEXICON_RU["cancel_deletion"],
            callback_data=f"cancel-expense-{expense_id}-deletion-{trip_id}",
        ),
    )
    return kb_builder.as_markup()


def base_expense_kb(
    trip_id: int,
    expense_id: int,
    debtor_username: str,
    is_admin: bool,
) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to
    write off the user's debt or open the expense info.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    if is_admin:
        kb_builder.row(
            InlineKeyboardButton(
                text=KB_LEXICON_RU["write_off_debt"],
                callback_data=f"write-off-debt-{expense_id}-debtor-{debtor_username}",
            ),
        )
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_expense"],
            callback_data=f"trip-{trip_id}-expense-{expense_id}-page-0",
        ),
    )
    return kb_builder.as_markup()


def confirm_write_off_kb(expense_id: int, debtor_username: str) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user
    to finally write off the debt.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["write_off"],
            callback_data=f"finally-write-off-{expense_id}-debtor-{debtor_username}",
        ),
        InlineKeyboardButton(
            text=KB_LEXICON_RU["cancel_write_off"],
            callback_data=f"cancel-expenses-{expense_id}-write-off",
        ),
    )
    return kb_builder.as_markup()


def back_to_expense_kb(trip_id: int, expense_id: int) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to go back to the expense section.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_expense"],
            callback_data=f"trip-{trip_id}-expense-{expense_id}-page-0",
        ),
    )
    return kb_builder.as_markup()


def back_to_expenses_kb(trip_id: int) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to go back to the expenses section.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_expenses"],
            callback_data=f"expenses-{trip_id}-page-0",
        ),
    )
    return kb_builder.as_markup()


def play_kb(trip_id: int, expense_id: int) -> InlineKeyboardMarkup:
    """
    Build a keyboard which allows the user to play a game.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["play"],
            callback_data=f"trip-{trip_id}-expense-{expense_id}-play",
        ),
    )
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back_to_expense"],
            callback_data=f"trip-{trip_id}-expense-{expense_id}-page-0",
        ),
    )
    return kb_builder.as_markup()
