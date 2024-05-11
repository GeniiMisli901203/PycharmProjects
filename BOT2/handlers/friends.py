from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from states import FSMFriend
from lexicon import LEXICON_RU, ERROR_LEXICON_RU
from services import invite_message, create_profile
from errors import DatabaseError, UserNotFoundError
from database import get_trip_db, add_friend_db, get_user_db, remove_friend_db
from keyboards import (
    paginator_kb,
    base_friend_kb,
    base_friends_kb,
    my_trips_kb,
    confirm_friend_deletion_kb,
    back_to_friends_kb,
    base_found_user_kb,
    back_found_users_kb,
)


friend_router: Router = Router()


@friend_router.callback_query(
    F.data.func(lambda x: "friends-" in x and "-page-" in x and x.count("-") == 3),
    StateFilter(default_state),
)
async def friends(
    callback: CallbackQuery,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Send friends in the trip.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        trip_id = int(data[1])
        trip = await get_trip_db(trip_id, sessionmaker)
        await callback.message.edit_text(
            LEXICON_RU["friends"],
            reply_markup=(
                await paginator_kb(
                    user,
                    int(data[-1]),
                    "friends",
                    sessionmaker,
                    user["username"] == trip["username"],
                    trip_id,
                )
            ),
        )
    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@friend_router.callback_query(
    F.data.func(lambda x: "-add-friend" in x), StateFilter(default_state)
)
async def invite_friend(callback: CallbackQuery, state: FSMContext):
    """
    Let the user invite his friend to the trip.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        await callback.message.edit_text(LEXICON_RU["add_friend"])
        await state.update_data(trip_id=int(data[1]))
        await state.set_state(FSMFriend.add_friend)
    except:
        await state.clear()
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@friend_router.message(StateFilter(FSMFriend.add_friend))
async def add_friend(
    message: Message,
    state: FSMContext,
    user: dict,
    bot: Bot,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Add the friend.
    """

    try:
        data = await state.get_data()
        trip_id = int(data["trip_id"])
        username = message.text.replace("@", "")

        if username != user["username"]:
            trip_name, friend_id = await add_friend_db(username, trip_id, sessionmaker)
            await message.answer(
                LEXICON_RU["friend_addition_done"],
                reply_markup=base_friends_kb(trip_id),
            )
            await state.clear()

            try:
                await bot.send_message(
                    friend_id,
                    invite_message(user["username"], trip_name),
                    reply_markup=my_trips_kb(),
                )
            except:
                pass

        else:
            await message.answer(ERROR_LEXICON_RU["cant_add_yourself"])

    except UserNotFoundError:
        await message.answer(ERROR_LEXICON_RU["UserNotFoundError"])
    except DatabaseError:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@friend_router.callback_query(
    F.data.func(lambda x: "-friend-" in x and "friends-" in x and x.count("-") == 3),
    StateFilter(default_state),
)
async def get_friend(
    callback: CallbackQuery,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Send the friend info with delete button.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        trip_id = int(data[1])
        friend_username = data[-1]
        trip = await get_trip_db(trip_id, sessionmaker)
        friend = await get_user_db(friend_username, sessionmaker)
        await callback.message.edit_text(
            create_profile(friend),
            reply_markup=base_friend_kb(
                trip_id,
                friend_username,
                user["username"] == trip["username"],
            ),
        )
    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@friend_router.callback_query(
    F.data.func(lambda x: "pre-delete-friends-" in x), StateFilter(default_state)
)
async def pre_delete_friend(callback: CallbackQuery):
    """
    Let the user remove the friend from the trip.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        await callback.message.answer(
            LEXICON_RU["confirm_deletion"],
            reply_markup=confirm_friend_deletion_kb(int(data[3]), data[-1]),
        )
    except:
        await callback.message.answer(ERROR_LEXICON_RU["InternalError"])


@friend_router.callback_query(
    F.data.func(lambda x: "finally-remove-friends-" in x), StateFilter(default_state)
)
async def finally_remove_friend(
    callback: CallbackQuery,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    try:
        await callback.answer()
        data = callback.data.split("-")
        trip_id = int(data[3])
        friend_username = data[-1]
        await remove_friend_db(friend_username, trip_id, sessionmaker)
        await callback.message.edit_text(
            LEXICON_RU["deletion_done"],
            reply_markup=back_to_friends_kb(trip_id),
        )
    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@friend_router.callback_query(
    F.data.func(lambda x: "cancel-friends-" in x),
    StateFilter(default_state),
)
async def cancel_friend_deletion(callback: CallbackQuery):
    try:
        await callback.answer()
        data = callback.data.split("-")
        await callback.message.edit_text(
            LEXICON_RU["deletion_canceled"],
            reply_markup=back_to_friends_kb(int(data[2])),
        )
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@friend_router.callback_query(
    F.data.func(lambda x: "found-users-" in x),
    StateFilter(default_state),
)
async def find_friends(
    callback: CallbackQuery,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Let the user find friends.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        trip_id = int(data[2])
        await callback.message.edit_text(
            LEXICON_RU["found_friends"],
            reply_markup=(
                await paginator_kb(
                    user,
                    int(data[-1]),
                    "find_friends",
                    sessionmaker,
                    trip_id=trip_id,
                )
            ),
        )
    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@friend_router.callback_query(
    F.data.func(lambda x: "-user-" in x and "-invite-" not in x),
    StateFilter(default_state),
)
async def get_found_user(
    callback: CallbackQuery,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Send the user info with "add to trip" button.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        trip_id = int(data[1])
        found_user_username = data[-1]
        trip = await get_trip_db(trip_id, sessionmaker)
        found_user = await get_user_db(found_user_username, sessionmaker)
        await callback.message.edit_text(
            create_profile(found_user),
            reply_markup=base_found_user_kb(
                trip_id,
                found_user_username,
                user["username"] == trip["username"],
            ),
        )
    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@friend_router.callback_query(
    F.data.func(lambda x: "-invite-user-" in x),
    StateFilter(default_state),
)
async def add_found_user(
    callback: CallbackQuery,
    bot: Bot,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Add the found user to the trip.
    """

    try:
        data = callback.data.split("-")
        trip_id = int(data[1])
        found_user_username = data[-1]
        trip_name, found_user_id = await add_friend_db(
            found_user_username, trip_id, sessionmaker
        )
        await callback.message.edit_text(
            LEXICON_RU["friend_addition_done"],
            reply_markup=back_found_users_kb(trip_id),
        )

        try:
            await bot.send_message(
                found_user_id,
                invite_message(user["username"], trip_name),
                reply_markup=my_trips_kb(),
            )
        except:
            pass
    except UserNotFoundError:
        await callback.message.edit_text(ERROR_LEXICON_RU["UserNotFoundError"])
    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])
