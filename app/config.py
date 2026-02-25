from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ACCESS_TOKEN_LT: int
    JWT_SECRET_KEY: str
    ENCRYPT_ALG: str
    API_HOST: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()