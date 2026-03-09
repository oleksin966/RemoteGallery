from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_DAYS: int
    PHOTOS_ROOT: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    DATABASE_URL: str
    THUMBS_DIR: str

    class Config:
        env_file = ".env"


settings = Settings()

# Создаём папку для кеша миниатюр
Path(settings.THUMBS_DIR).mkdir(parents=True, exist_ok=True)
