from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ACCESS_TOKEN_LT: int
    JWT_SECRET_KEY: str
    ENCRYPT_ALG: str
    DB_PATH: str | None
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    LOG_FILE: str | None = ""
    model_config = SettingsConfigDict(env_file=".env")

    @property
    def database_url(self):
        return f"sqlite+aiosqlite:///{self.DB_PATH}"

settings = Settings()
