# app/main.py
import asyncio
from aiogram import Dispatcher
from aiogram.types import BotCommand
from app.bot.instance import bot, dp
from app.handlers.user import router as user_router
from app.handlers.payment import router as payment_router
from app.handlers.admin import router as admin_router
from app.config.settings import settings
from app.utils.logger import configure_logger, logger
from app.database.session import engine
from app.database.models import Base
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.scheduler.tasks import check_expired_subscriptions, send_expiration_notifications

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
