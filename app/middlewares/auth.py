# app/middlewares/auth.py
from typing import Any, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from app.config.settings import settings

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler,
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Проверяем, является ли пользователь администратором
        user = getattr(event, 'from_user', None)
        if user:
            is_admin = user.id in settings.ADMIN_IDS
            data["is_admin"] = is_admin
            
        return await handler(event, data)
