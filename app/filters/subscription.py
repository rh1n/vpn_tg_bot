# app/filters/subscription.py
from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery

class IsSubscriptionActionFilter(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        # Проверяем, что callback_data начинается с префикса действия
        return callback.data and any(
            callback.data.startswith(prefix) 
            for prefix in ["renew:", "get_link:", "delete:", "confirm_delete:"]
        )
