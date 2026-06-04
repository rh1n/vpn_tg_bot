# app/config/settings.py
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    BOT_TOKEN: str
    POSTGRES_DSN: str
    PANEL_URL: str
    PANEL_USERNAME: str
    PANEL_PASSWORD: str
    PANEL_INBOUND_ID: int
    ADMIN_IDS: str
    SUPPORT_USERNAME: str
    LOCALE_DEFAULT: str = "ru"
    STARS_PRICE: int = 100

    @validator("ADMIN_IDS")
    def parse_admin_ids(cls, v: str) -> List[int]:
        return [int(x.strip()) for x in v.split(",") if x.strip()]

    @validator("LOCALE_DEFAULT")
    def validate_locale(cls, v: str) -> str:
        if v not in ["ru", "en"]:
            raise ValueError("LOCALE_DEFAULT must be either 'ru' or 'en'")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
