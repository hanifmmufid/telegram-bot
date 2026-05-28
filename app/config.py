from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    BOT_TOKEN: str

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()