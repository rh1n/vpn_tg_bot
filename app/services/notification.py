# app/services/notification.py
import asyncio
from typing import List
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User
from app.config.settings import settings
from app.utils.logger import logger

class NotificationService:
    def __init__(self, bot: Bot, db_session: AsyncSession):
        self.bot = bot
        self.db_session = db_session

    async def send_message_to_user(self, user_id: int, text: str, parse_mode: str = "HTML") -> bool:
        """Отправка сообщения пользователю"""
        try:
            await self.bot.send_message(user_id, text, parse_mode=parse_mode)
            return True
        except Exception as e:
            logger.warning(f"Failed to send message to user {user_id}: {e}")
            return False

    async def broadcast_message(self, text: str, parse_mode: str = "HTML") -> int:
        """Массовая рассылка сообщения всем пользователям"""
        try:
            # Получаем всех пользователей
            result = await self.db_session.execute(User.__table__.select())
            users = result.fetchall()
            
            sent_count = 0
            for user in users:
                try:
                    await self.bot.send_message(user.telegram_id, text, parse_mode=parse_mode)
                    sent_count += 1
                    # Небольшая задержка чтобы не превысить лимиты Telegram
                    await asyncio.sleep(0.05)
                except Exception as e:
                    logger.warning(f"Failed to send message to user {user.telegram_id}: {e}")
                    continue
                    
            logger.info(f"Broadcast sent to {sent_count} users")
            return sent_count
        except Exception as e:
            logger.error(f"Error during broadcast: {e}")
            return 0

    async def notify_admins(self, text: str, parse_mode: str = "HTML") -> None:
        """Уведомление администраторов"""
        for admin_id in settings.ADMIN_IDS:
            try:
                await self.bot.send_message(admin_id, text, parse_mode=parse_mode)
            except Exception as e:
                logger.warning(f"Failed to notify admin {admin_id}: {e}")
