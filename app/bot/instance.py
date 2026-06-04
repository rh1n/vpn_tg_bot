# app/bot/instance.py
import sys
import os

# Добавляем корневую директорию в путь Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config.settings import settings
from middlewares.db import DBSessionMiddleware
from middlewares.i18n import I18nMiddleware
from middlewares.auth import AuthMiddleware

# Создаем экземпляр бота
bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)

# Создаем диспетчер
dp = Dispatcher()

# Регистрируем middleware
dp.update.outer_middleware(DBSessionMiddleware())
dp.update.outer_middleware(I18nMiddleware())
dp.update.outer_middleware(AuthMiddleware())
