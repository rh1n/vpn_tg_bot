# app/middlewares/db.py
from typing import Any, Dict, Optional
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from app.database.session import async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession

class DBSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler,
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with async_session_maker() as session:
            data["db_session"] = session
            return await handler(event, data)
