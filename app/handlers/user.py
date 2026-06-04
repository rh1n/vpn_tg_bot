# app/handlers/user.py
import sys
import os

# Добавляем корневую директорию в путь Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from keyboards.inline import main_menu_keyboard, back_keyboard, vpn_actions_keyboard, confirm_delete_keyboard
from repositories.base import UserRepository, VPNClientRepository, SubscriptionRepository
from config.settings import settings
from datetime import datetime, timedelta
from database.models import SubscriptionStatus
import asyncio

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message, gettext) -> None:
    """Обработчик команды /start"""
    # Сохраняем пользователя в БД
    user_repo = UserRepository(message.db_session)
    await user_repo.create_or_update_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        language_code=message.from_user.language_code or settings.LOCALE_DEFAULT
    )
    
    # Отправляем приветственное сообщение
    await message.answer(
        gettext("start_message"),
        reply_markup=main_menu_keyboard(gettext)
    )

@router.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: CallbackQuery, gettext) -> None:
    """Обработчик главного меню"""
    await callback.message.edit_text(
        gettext("main_menu"),
        reply_markup=main_menu_keyboard(gettext)
    )
    await callback.answer()

@router.callback_query(F.data == "buy_vpn")
async def buy_vpn_handler(callback: CallbackQuery, gettext) -> None:
    """Обработчик покупки VPN"""
    from aiogram.types import LabeledPrice
    
    # Отправляем инвойс
    prices = [LabeledPrice(label="VPN Subscription", amount=settings.STARS_PRICE)]
    
    await callback.bot.send_invoice(
        chat_id=callback.from_user.id,
        title="VPN Access",
        description=gettext("payment_description"),
        prices=prices,
        provider_token="",  # Для Stars токен не нужен
        currency="XTR",  # Telegram Stars
        payload=f"vpn_subscription_{callback.from_user.id}_{int(datetime.utcnow().timestamp())}"
    )
    
    await callback.answer()

@router.callback_query(F.data == "my_vpns")
async def my_vpns_handler(callback: CallbackQuery, gettext) -> None:
    """Обработчик раздела 'Мои VPN'"""
    # Получаем VPN клиентов пользователя
    vpn_repo = VPNClientRepository(callback.db_session)
    vpn_clients = await vpn_repo.get_vpn_clients_by_user_id(callback.from_user.id)
    
    if not vpn_clients:
        await callback.message.edit_text(
            gettext("no_vpns"),
            reply_markup=back_keyboard(gettext)
        )
        await callback.answer()
        return
    
    # Получаем подписки для клиентов
    sub_repo = SubscriptionRepository(callback.db_session)
    
    text = gettext("your_vpns") + "\n\n"
    
    for client in vpn_clients:
        # Получаем подписку клиента
        result = await callback.db_session.execute(
            "SELECT * FROM subscriptions WHERE vpn_client_id = :client_id ORDER BY created_at DESC LIMIT 1",
            {"client_id": client.id}
        )
        subscription = result.fetchone()
        
        if subscription:
            # Вычисляем количество оставшихся дней
            days_left = (subscription.expire_at - datetime.utcnow()).days
            status_text = gettext("active") if subscription.status == SubscriptionStatus.ACTIVE else gettext("expired")
            
            text += gettext("vpn_info", 
                          email=client.email,
                          status=status_text,
                          expire_date=subscription.expire_at.strftime("%d.%m.%Y"),
                          days_left=days_left) + "\n\n"
        
        # Добавляем кнопки действий для каждого клиента
        keyboard = vpn_actions_keyboard(gettext, client.id)
        
        # Отправляем информацию о клиенте отдельным сообщением
        await callback.message.answer(
            text,
            reply_markup=keyboard
        )
        text = ""  # Очищаем текст для следующего клиента
    
    if text:  # Если остался текст (в случае одной записи)
        await callback.message.answer(
            text,
            reply_markup=back_keyboard(gettext)
        )
    
    await callback.message.delete()
    await callback.answer()

@router.callback_query(F.data == "instructions")
async def instructions_handler(callback: CallbackQuery, gettext) -> None:
    """Обработчик инструкции"""
    await callback.message.edit_text(
        gettext("instructions_text"),
        reply_markup=back_keyboard(gettext)
    )
    await callback.answer()

@router.callback_query(F.data == "support")
async def support_handler(callback: CallbackQuery, gettext) -> None:
    """Обработчик поддержки"""
    await callback.message.edit_text(
        gettext("support_text", support=settings.SUPPORT_USERNAME),
        reply_markup=back_keyboard(gettext)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("get_link:"))
async def get_link_handler(callback: CallbackQuery, gettext) -> None:
    """Обработчик получения ссылки"""
    client_id = int(callback.data.split(":")[1])
    
    # Получаем VPN клиента
    vpn_repo = VPNClientRepository(callback.db_session)
    client = await vpn_repo.get_vpn_client_by_id(client_id)
    
    if not client or client.user_id != callback.from_user.id:
        await callback.answer(gettext("vpn_not_found"), show_alert=True)
        return
    
    # Отправляем ссылку пользователю
    # В реальной реализации здесь должна быть расшифровка ссылки
    await callback.message.answer(
        gettext("vpn_created", link=client.connection_link),
        reply_markup=back_keyboard(gettext)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("delete:"))
async def delete_handler(callback: CallbackQuery, gettext) -> None:
    """Обработчик удаления VPN"""
    client_id = int(callback.data.split(":")[1])
    
    # Подтверждение удаления
    keyboard = confirm_delete_keyboard(gettext, client_id)
    
    await callback.message.edit_text(
        gettext("confirm_delete"),
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_delete:"))
async def confirm_delete_handler(callback: CallbackQuery, gettext) -> None:
    """Обработчик подтверждения удаления"""
    from services.xui import XUIService
    
    if callback.data.startswith("confirm_delete:"):
        client_id = int(callback.data.split(":")[1])
        
        # Получаем VPN клиента
        vpn_repo = VPNClientRepository(callback.db_session)
        client = await vpn_repo.get_vpn_client_by_id(client_id)
        
        if not client or client.user_id != callback.from_user.id:
            await callback.answer(gettext("vpn_not_found"), show_alert=True)
            return
        
        # Удаляем клиента из панели 3x-ui
        async with XUIService() as xui:
            success = await xui.delete_client(str(client.uuid))
        
        if success:
            # Удаляем из БД
            await vpn_repo.delete_vpn_client(client_id)
            await callback.message.edit_text(
                gettext("vpn_deleted"),
                reply_markup=back_keyboard(gettext)
            )
        else:
            await callback.answer(gettext("error_occurred"), show_alert=True)
    else:
        # Отмена удаления
        await callback.message.edit_text(
            gettext("main_menu"),
            reply_markup=main_menu_keyboard(gettext)
        )
    
    await callback.answer()
