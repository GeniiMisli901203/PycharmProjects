from asyncio import sleep
from random import choice

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from states import FSMExpense
from lexicon import LEXICON_RU, KB_LEXICON_RU, ERROR_LEXICON_RU
from services import create_expense_info, debtor_message, create_debtor_info
from keyboards import (
    paginator_kb,
    base_expenses_kb,
    my_trips_kb,
    base_expense_kb,
    confirm_write_off_kb,
    back_to_expense_kb,
    back_to_expenses_kb,
    leave_same_kb,
    confirm_expense_deletion_kb,
    play_kb,
)
from database import (
    create_update_expense_db,
    get_expense_db,
    get_user_db,
    add_debtor_db,
    delete_expense_db,
    write_off_debt_db,
    loser_db,
)
from errors import (
    DatabaseError,
    UserNotFoundError,
    UserNotInTripError,
    ServiceConnectionError,
)


expense_router: Router = Router()


@expense_router.callback_query(
    F.data.func(lambda x: "expenses-" in x and "-page-" in x),
    StateFilter(default_state),
)
async def expenses(
    callback: CallbackQuery,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Send the expenses.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        await callback.message.edit_text(
            LEXICON_RU["expenses"],
            reply_markup=(
                await paginator_kb(
                    user, int(data[-1]), "expenses", sessionmaker, trip_id=int(data[1])
                )
            ),
        )
    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@expense_router.callback_query(
    F.data.func(lambda x: "-new-expense" in x),
    StateFilter(default_state),
)
async def new_expense(callback: CallbackQuery, user: dict, state: FSMContext):
    """
    Let the user enter the cost.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        await callback.message.edit_text(LEXICON_RU["new_expense"])
        await state.update_data(
            trip_id=int(data[1]), username=user["username"], currency=user["currency"]
        )
        await state.set_state(FSMExpense.set_name)
    except:
        await state.clear()
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@expense_router.message(
    F.text,
    StateFilter(FSMExpense.set_name),
)
async def expense_name(message: Message, state: FSMContext):
    """
    Set expense name and let the user enter cost.
    """

    try:
        await message.answer(LEXICON_RU["expense_cost"])
        await state.update_data(name=message.text)
        await state.set_state(FSMExpense.set_cost)
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@expense_router.message(
    F.text,
    StateFilter(FSMExpense.set_cost),
)
async def expense_cost(message: Message, state: FSMContext):
    """
    Set expense cost and let the user enter the list of debtors.
    """

    try:
        cost = float(message.text.replace(",", "."))
        await message.answer(LEXICON_RU["expense_debtors"])
        await state.update_data(cost=cost)
        await state.set_state(FSMExpense.set_debtors)
    except ValueError:
        await message.answer(ERROR_LEXICON_RU["incorrect_data"])
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@expense_router.message(
    F.text,
    StateFilter(FSMExpense.set_debtors),
)
async def expense_debtors(
    message: Message,
    state: FSMContext,
    bot: Bot,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Set the expense debtors list.
    """

    try:
        if "@" in message.text:
            data = await state.get_data()
            data["debtors"] = message.text.replace("@", "").split(", ")
            debtors, trip_name = await create_update_expense_db(data, sessionmaker)
            await message.answer(
                LEXICON_RU["expense_added"],
                reply_markup=base_expenses_kb(data["trip_id"]),
            )
            await state.clear()

            for debtor_id in debtors:
                try:
                    await bot.send_message(
                        debtor_id,
                        debtor_message(user["username"], trip_name, data["name"]),
                        reply_markup=my_trips_kb(),
                    )
                except:
                    pass
        else:
            await message.answer(ERROR_LEXICON_RU["incorrect_data"])

    except UserNotFoundError:
        await message.answer(ERROR_LEXICON_RU["UserInListNotFoundError"])
    except UserNotInTripError:
        await message.answer(ERROR_LEXICON_RU["UserNotInTripError"])
    except DatabaseError:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@expense_router.callback_query(
    F.data.func(lambda x: "expense-" in x and "-page-" in x),
    StateFilter(default_state),
)
async def expense(
    callback: CallbackQuery,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Send the debtors list with add and back button.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        expense_id = int(data[3])
        expense_db = await get_expense_db(expense_id, sessionmaker)
        await callback.message.edit_text(
            create_expense_info(expense_db),
            reply_markup=await paginator_kb(
                user,
                int(data[-1]),
                "expense_debtors",
                sessionmaker,
                expense_db["username"] == user["username"],
                int(data[1]),
                expense_id,
            ),
        )
    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@expense_router.callback_query(
    F.data.func(lambda x: "-new-debtor" in x),
    StateFilter(default_state),
)
async def new_debtor(callback: CallbackQuery, state: FSMContext):
    """
    Let the user add his trip friend to the debtors list.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        await callback.message.edit_text(LEXICON_RU["new_debtor"])
        await state.update_data(expense_id=int(data[1]))
        await state.set_state(FSMExpense.add_debtor)
    except:
        await state.clear()
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@expense_router.message(F.text, StateFilter(FSMExpense.add_debtor))
async def add_debtor(
    message: Message,
    state: FSMContext,
    bot: Bot,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Add the debtor to list.
    """

    try:
        if "@" in message.text:
            data = await state.get_data()
            data["debtor"] = message.text.replace("@", "")
            debtor_id, trip_name, trip_id = await add_debtor_db(data, sessionmaker)
            await message.answer(
                LEXICON_RU["debtor_added"],
                reply_markup=back_to_expense_kb(trip_id, data["expense_id"]),
            )
            await state.clear()

            try:
                await bot.send_message(
                    debtor_id,
                    debtor_message(user["username"], trip_name, data["name"]),
                    reply_markup=my_trips_kb(),
                )
            except:
                pass
        else:
            await message.answer(ERROR_LEXICON_RU["incorrect_data"])

    except UserNotFoundError:
        await message.answer(ERROR_LEXICON_RU["UserInListNotFoundError"])
    except UserNotInTripError:
        await message.answer(ERROR_LEXICON_RU["UserNotInTripError"])
    except DatabaseError:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@expense_router.callback_query(
    F.data.func(lambda x: "edit-expenses-" in x),
    StateFilter(default_state),
)
async def edit_expense(callback: CallbackQuery, user: dict, state: FSMContext):
    """
    Let the user edit the cost.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        await callback.message.answer(
            LEXICON_RU["edit_expense"], reply_markup=leave_same_kb()
        )
        await state.update_data(
            expense_id=int(data[-1]),
            username=user["username"],
            currency=user["currency"],
        )
        await state.set_state(FSMExpense.edit_name)
    except:
        await state.clear()
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@expense_router.message(
    F.text,
    StateFilter(FSMExpense.edit_name),
)
async def edit_name(message: Message, state: FSMContext):
    """
    Edit the expense name and let the user edit the cost.
    """

    try:
        if message.text != KB_LEXICON_RU["leave_same"]:
            await state.update_data(name=message.text)

        await message.answer(LEXICON_RU["edit_cost"], reply_markup=leave_same_kb())
        await state.set_state(FSMExpense.edit_cost)
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@expense_router.message(
    F.text,
    StateFilter(FSMExpense.edit_cost),
)
async def edit_cost(
    message: Message,
    state: FSMContext,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Edit expense cost and send "back to expense" button.
    """

    try:
        data = await state.get_data()
        expense_id = data["expense_id"]

        if message.text != KB_LEXICON_RU["leave_same"]:
            data["cost"] = float(message.text.replace(",", "."))

        trip_id = await create_update_expense_db(data, sessionmaker)

        await message.answer(
            LEXICON_RU["editing_done"],
            reply_markup=back_to_expense_kb(trip_id, expense_id),
        )
        await state.clear()
    except ValueError:
        await message.answer(ERROR_LEXICON_RU["incorrect_data"])
    except DatabaseError:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@expense_router.callback_query(
    F.data.func(lambda x: "-game" in x),
    StateFilter(default_state),
)
async def expense_game(callback: CallbackQuery):
    """
    Let the user play a game, all debts are credited to the loser.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        await callback.message.edit_text(
            LEXICON_RU["play_game"],
            reply_markup=play_kb(int(data[1]), int(data[-2])),
        )
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@expense_router.callback_query(
    F.data.func(lambda x: "-play" in x),
    StateFilter(default_state),
)
async def play_expense_game(
    callback: CallbackQuery,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Pick a loser.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        expense_id = int(data[-2])
        expense_db = await get_expense_db(expense_id, sessionmaker)
        await callback.message.answer_dice()
        loser = choice((expense_db["username"], *expense_db["debtors"]))
        await sleep(4)
        await callback.message.answer(
            "\U00002620 Проиграл" + f" @{loser} " + LEXICON_RU["game_loser"],
            reply_markup=back_to_expenses_kb(int(data[1])),
        )
        await loser_db(loser, expense_id, sessionmaker)
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@expense_router.callback_query(
    F.data.func(lambda x: "pre-delete-expenses-" in x), StateFilter(default_state)
)
async def pre_delete_expense(callback: CallbackQuery):
    """
    Let the user delete the expense.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        await callback.message.edit_text(
            LEXICON_RU["confirm_deletion"],
            reply_markup=confirm_expense_deletion_kb(int(data[-3]), int(data[-1])),
        )
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@expense_router.callback_query(
    F.data.func(lambda x: "finally-remove-expense-" in x), StateFilter(default_state)
)
async def finally_delete_expense(
    callback: CallbackQuery,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    try:
        await callback.answer()
        data = callback.data.split("-")
        await delete_expense_db(int(data[-3]), sessionmaker)
        await callback.message.edit_text(
            LEXICON_RU["deletion_done"],
            reply_markup=back_to_expenses_kb(int(data[-1])),
        )
    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@expense_router.callback_query(
    F.data.func(lambda x: "cancel-expense-" in x),
    StateFilter(default_state),
)
async def cancel_expense_deletion(callback: CallbackQuery):
    try:
        await callback.answer()
        data = callback.data.split("-")
        await callback.message.edit_text(
            LEXICON_RU["deletion_canceled"],
            reply_markup=back_to_expense_kb(int(data[-1]), int(data[-3])),
        )
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@expense_router.callback_query(
    F.data.func(lambda x: "expense-" in x and "-debtor-" in x),
    StateFilter(default_state),
)
async def get_debtor(
    callback: CallbackQuery,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Send the debtor info with different buttons.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        expense_id = int(data[1])
        username = data[-1]
        expense_db = await get_expense_db(expense_id, sessionmaker)
        debtor = await get_user_db(username, sessionmaker)
        await callback.message.edit_text(
            await create_debtor_info(debtor, expense_db),
            reply_markup=base_expense_kb(
                expense_db["trip_id"],
                expense_id,
                username,
                expense_db["username"] == user["username"],
            ),
        )
    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except ServiceConnectionError:
        await callback.message.edit_text(ERROR_LEXICON_RU["ServiceConnectionError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@expense_router.callback_query(
    F.data.func(lambda x: "write-off-debt-" in x), StateFilter(default_state)
)
async def pre_write_off(callback: CallbackQuery):
    """
    Let the user write off the debt.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        await callback.message.edit_text(
            LEXICON_RU["confirm_write_off"],
            reply_markup=confirm_write_off_kb(int(data[3]), data[-1]),
        )
    except:
        await callback.message.answer(ERROR_LEXICON_RU["InternalError"])


@expense_router.callback_query(
    F.data.func(lambda x: "finally-write-off-" in x), StateFilter(default_state)
)
async def finally_write_off(
    callback: CallbackQuery,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    try:
        await callback.answer()
        data = callback.data.split("-")
        expense_id = int(data[3])
        debtor_username = data[-1]
        trip_id, is_closed = await write_off_debt_db(
            debtor_username, expense_id, sessionmaker
        )

        if is_closed:
            await callback.message.edit_text(
                LEXICON_RU["write_off_done_closed"],
                reply_markup=back_to_expenses_kb(trip_id),
            )
        else:
            await callback.message.edit_text(
                LEXICON_RU["write_off_done"],
                reply_markup=back_to_expense_kb(trip_id, expense_id),
            )
    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@expense_router.callback_query(
    F.data.func(lambda x: "cancel-expenses-" in x),
    StateFilter(default_state),
)
async def cancel_write_off(
    callback: CallbackQuery,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    try:
        await callback.answer()
        data = callback.data.split("-")
        expense_id = int(data[2])
        expense = await get_expense_db(expense_id, sessionmaker)
        await callback.message.edit_text(
            LEXICON_RU["write_off_canceled"],
            reply_markup=back_to_expense_kb(expense["trip_id"], expense_id),
        )
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])
