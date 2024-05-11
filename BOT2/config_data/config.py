from dataclasses import dataclass
from asyncio import BoundedSemaphore

from environs import Env
from cashews import Cache, cache
from openrouteservice import Client


__all__ = ["Config", "load_config"]


@dataclass
class TgBot:
    token: str
    cache: Cache
    semaphore: BoundedSemaphore
    openrouteservice: Client
    geoapify: str


@dataclass
class PostgresConfig:
    driver: str
    user: str
    password: str
    host: str
    port: int
    database: str


@dataclass
class RedisConfig:
    host: str
    port: int


@dataclass
class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    tg_bot: TgBot
    postgres: PostgresConfig
    redis: RedisConfig


def load_config() -> Config:
    """
    Create the bot config class.
    """

    env: Env = Env()
    env.read_env()
    redis_host = env("REDIS_HOST")
    redis_port = int(env("REDIS_PORT"))

    cache.setup(f"redis://{redis_host}:{redis_port}/1", client_side=True)

    return Config(
        tg_bot=TgBot(
            token=env("7039618462:AAESr2bt7kk8cyC3lGi93fHT1COZFIdPsGQ"),
            cache=cache,
            semaphore=BoundedSemaphore(20),
            openrouteservice=Client(key=env("5b3ce3597851110001cf624839f02112373e4314b5da120a3dfab568")),
            geoapify=env("d3c77a426a0b476eab1e8c86cc84cd95"),
        ),
        postgres=PostgresConfig(
            driver=env("POSTGRES_DRIVER"),
            user=env("POSTGRES_USER"),
            password=env("POSTGRES_PASSWORD"),
            host=env("POSTGRES_HOST"),
            port=int(env("POSTGRES_PORT")),
            database=env("POSTGRES_DB"),
        ),
        redis=RedisConfig(host=redis_host, port=redis_port),
    )
