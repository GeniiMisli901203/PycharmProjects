import datetime
from typing import Callable, Awaitable, Any

from cashews import Cache
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from config_data import Config, load_config
from database import User, get_postgres_sessionmaker


config: Config = load_config()
cache: Cache = config.tg_bot.cache


class AuthMiddleware(BaseMiddleware):
    """
    Get user from the db.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            tg_user_id = event.from_user.id
            cached_user = await cache.get(f"user-{tg_user_id}")

            if not cached_user:
                async with get_postgres_sessionmaker()() as session:
                    async with session.begin():
                        user = await session.get(User, tg_user_id)

                        if user:
                            await cache.set(
                                f"user-{tg_user_id}", user.columns_to_dict(), "1h"
                            )
                            user = user.columns_to_dict()
            else:
                user = cached_user

            data["user"] = user
            return await handler(event, data)


class AntiFloodMiddleware(BaseMiddleware):
    """
    Antiflood protection
    """

    time_updates: dict[int, datetime.datetime] = {}
    timedelta_limiter: datetime.timedelta = datetime.timedelta(seconds=0.5)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id
            if user_id in self.time_updates:
                if (
                    datetime.datetime.now() - self.time_updates[user_id]
                ) > self.timedelta_limiter:
                    self.time_updates[user_id] = datetime.datetime.now()
                    return await handler(event, data)
            else:
                self.time_updates[user_id] = datetime.datetime.now()
                return await handler(event, data)
