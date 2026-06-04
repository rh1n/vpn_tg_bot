# app/handlers/admin.py
import sys
import os

# Добавляем корневую директорию в путь Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy import func
from filters.admin import IsAdminFilter
from keyboards.inline import admin_menu_keyboard, back_keyboard
from repositories.base import UserRepository, VPNClientRepository, SubscriptionRepository, PaymentRepository
from services.notification import NotificationService
from database.models import SubscriptionStatus
from utils.logger import logger

router = Router()
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())

class AdminStates(StatesGroup):
    waiting_for_broadcast_message = State()

@router.message(Command("admin"))
async def admin_handler(message: Message, gettext) -> None:
    """Обработчик команды /admin"""
    await message.answer(
        gettext("admin_panel"),
        reply_markup=admin_menu_keyboard(gettext)
    )

@router.callback_query(F.data == "admin_stats")
async def admin_stats_handler(callback: CallbackQuery, gettext) -> None:
    """Обработчик статистики"""
    # Получаем статистику
    user_count = await callback.db_session.scalar(func.count(UserRepository.__table__.c.id))
    
    # Активные ключи
    active_sub_count = await callback.db_session.scalar(
        func.count(SubscriptionRepository.__table__.c.id)
        .where(SubscriptionRepository.__table__.c.status == SubscriptionStatus.ACTIVE)
    )
    
    # Доход
    total_revenue = await callback.db_session.scalar(
        func.sum(PaymentRepository.__table__.c.stars_amount)
    ) or 0
    
    await callback.message.edit_text(
        gettext("admin_stats", 
                users=user_count,
                active_keys=active_sub_count,
                revenue=total_revenue),
        reply_markup=admin_menu_keyboard(gettext)
    )
    await callback.answer()

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_handler(callback: CallbackQuery, gettext, state: FSMContext) -> None:
    """Обработчик рассылки"""
    await callback.message.edit_text(
        gettext("enter_broadcast_message"),
        reply_markup=back_keyboard(gettext)
    )
    await state.set_state(AdminStates.waiting_for_broadcast_message)
    await callback.answer()

@router.message(AdminStates.waiting_for_broadcast_message)
async def broadcast_message_handler(message: Message, gettext, state: FSMContext) -> None:
    """Обработчик сообщения для рассылки"""
    if not message.text:
        await message.answer(gettext("invalid_action"))
        return
    
    # Отправляем рассылку
    notification_service = NotificationService(message.bot, message.db_session)
    count = await notification_service.broadcast_message(message.text)
    
    await message.answer(
        gettext("broadcast_sent", count=count),
        reply_markup=admin_menu_keyboard(gettext)
    )
    
    await state.clear()
