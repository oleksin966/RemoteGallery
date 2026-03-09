from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    PHOTOS_ROOT: str = r"F:\Приват"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "changeme"
    DATABASE_URL: str = "sqlite:///./gallery.db"
    THUMBS_DIR: str = "./cache/thumbs"

    class Config:
        env_file = ".env"


settings = Settings()

# Создаём папку для кеша миниатюр
Path(settings.THUMBS_DIR).mkdir(parents=True, exist_ok=True)
