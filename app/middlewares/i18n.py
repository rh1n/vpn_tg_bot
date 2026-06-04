# app/middlewares/i18n.py
import json
import os
from typing import Any, Dict, Optional
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from app.config.settings import settings

class I18nMiddleware(BaseMiddleware):
    def __init__(self, locales_dir: str = "app/locales"):
        self.locales_dir = locales_dir
        self.translations: Dict[str, Dict[str, str]] = {}
        self.load_translations()

    def load_translations(self) -> None:
        """Загрузка переводов из файлов"""
        for filename in os.listdir(self.locales_dir):
            if filename.endswith(".json"):
                lang = filename[:-5]  # Убираем .json
                with open(os.path.join(self.locales_dir, filename), "r", encoding="utf-8") as f:
                    self.translations[lang] = json.load(f)

    def get_text(self, key: str, language: str, **kwargs) -> str:
        """Получение переведенного текста"""
        # Пытаемся получить перевод для запрашиваемого языка
        if language in self.translations and key in self.translations[language]:
            text = self.translations[language][key]
        # Если нет, используем язык по умолчанию
        elif settings.LOCALE_DEFAULT in self.translations and key in self.translations[settings.LOCALE_DEFAULT]:
            text = self.translations[settings.LOCALE_DEFAULT][key]
        # Если и это не удалось, возвращаем ключ
        else:
            text = key
            
        # Форматируем текст с параметрами
        if kwargs:
            text = text.format(**kwargs)
            
        return text

    async def __call__(
        self,
        handler,
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Определяем язык пользователя
        user_language = settings.LOCALE_DEFAULT
        
        if hasattr(event, 'from_user') and event.from_user:
            user_lang = event.from_user.language_code
            if user_lang and user_lang in self.translations:
                user_language = user_lang
            elif settings.LOCALE_DEFAULT in self.translations:
                user_language = settings.LOCALE_DEFAULT

        # Добавляем функцию перевода в данные
        data["gettext"] = lambda key, **kwargs: self.get_text(key, user_language, **kwargs)
        
        return await handler(event, data)
