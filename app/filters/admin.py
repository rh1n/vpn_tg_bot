# app/filters/admin.py
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from app.config.settings import settings

class IsAdminFilter(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user = event.from_user
        return user.id in settings.ADMIN_IDS
