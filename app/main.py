# app/main.py
import asyncio
import sys
import os

# Добавляем корневую директорию в путь Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Dispatcher
from aiogram.types import BotCommand
from bot.instance import bot, dp
from handlers.user import router as user_router
from handlers.payment import router as payment_router
from handlers.admin import router as admin_router
from config.settings import settings
from utils.logger import configure_logger, logger
from database.session import engine
from database.models import Base
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scheduler.tasks import check_expired_subscriptions, send_expiration_notifications

# Настраиваем логирование
configure_logger()

# Регистрируем роутеры
dp.include_router(user_router)
dp.include_router(payment_router)
dp.include_router(admin_router)

async def set_bot_commands():
    """Установка команд бота"""
    commands = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="admin", description="Админ панель"),
    ]
    await bot.set_my_commands(commands)

async def on_startup():
    """Действия при запуске бота"""
    logger.info("Starting bot...")
    
    # Создаем таблицы в БД
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Устанавливаем команды бота
    await set_bot_commands()
    
    logger.info("Bot started successfully")

async def on_shutdown():
    """Действия при остановке бота"""
    logger.info("Shutting down bot...")
    await bot.session.close()
    await engine.dispose()
    logger.info("Bot shut down successfully")

def setup_scheduler():
    """Настройка планировщика задач"""
    scheduler = AsyncIOScheduler()
    
    # Проверка истекших подписок каждый час
    scheduler.add_job(
        check_expired_subscriptions,
        'interval',
        hours=1,
        args=[dp['db_session'], bot]
    )
    
    # Уведомления за 3 дня до окончания
    scheduler.add_job(
        send_expiration_notifications,
        'interval',
        days=1,
        args=[dp['db_session'], bot, 3]
    )
    
    # Уведомления за 1 день до окончания
    scheduler.add_job(
        send_expiration_notifications,
        'interval',
        days=1,
        args=[dp['db_session'], bot, 1]
    )
    
    scheduler.start()
    return scheduler

async def main():
    """Главная функция бота"""
    try:
        # Регистрируем обработчики запуска и остановки
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # Настраиваем планировщик
        scheduler = setup_scheduler()
        
        # Запускаем бота
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        # Останавливаем планировщик
        if 'scheduler' in locals():
            scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
