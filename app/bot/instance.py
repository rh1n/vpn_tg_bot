# app/bot/instance.py
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from app.config.settings import settings
from app.middlewares.db import DBSessionMiddleware
from app.middlewares.i18n import I18nMiddleware
from app.middlewares.auth import AuthMiddleware

# Создаем экземпляр бота
bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)

# Создаем диспетчер
dp = Dispatcher()

# Регистрируем middleware
dp.update.outer_middleware(DBSessionMiddleware())
dp.update.outer_middleware(I18nMiddleware())
dp.update.outer_middleware(AuthMiddleware())
