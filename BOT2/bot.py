import asyncio
import logging

from redis.asyncio import Redis
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from config_data import Config, load_config
from database import get_postgres_sessionmaker
from handlers import main_router
from keyboards import set_main_menu


logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)-6s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger.info("Starting bot")

    config: Config = load_config()
    properties: DefaultBotProperties = DefaultBotProperties(parse_mode="HTML")

    storage: RedisStorage = RedisStorage(
        redis=Redis(host=config.redis.host, port=config.redis.port)
    )

    bot: Bot = Bot(token=config.tg_bot.token, default=properties)
    disp: Dispatcher = Dispatcher(storage=storage)
    disp.include_router(main_router)

    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await disp.start_polling(bot, sessionmaker=get_postgres_sessionmaker())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error("Bot stopped!")
        print(e)
