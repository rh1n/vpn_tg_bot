# app/handlers/payment.py
from aiogram import Router, F
from aiogram.types import PreCheckoutQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import UserRepository, VPNClientRepository, SubscriptionRepository, PaymentRepository
from app.services.xui import XUIService
from app.services.payment import PaymentService
from datetime import datetime, timedelta
from app.utils.logger import logger

router = Router()

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery) -> None:
    """Обработчик предварительной проверки оплаты"""
    # Здесь можно добавить дополнительные проверки
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, gettext) -> None:
    """Обработчик успешной оплаты"""
    from app.keyboards.inline import back_keyboard
    
    # Проверяем, не была ли эта оплата уже обработана
    payment_repo = PaymentRepository(message.db_session)
    payment_service = PaymentService(message.db_session)
    
    telegram_payment_charge_id = message.successful_payment.telegram_payment_charge_id
    
    if await payment_repo.is_payment_exists(telegram_payment_charge_id):
        logger.warning(f"Payment {telegram_payment_charge_id} already processed")
        await message.answer(gettext("payment_success"))
        return
    
    # Создаем запись об оплате
    user_repo = UserRepository(message.db_session)
    user = await user_repo.get_user_by_telegram_id(message.from_user.id)
    
    if not user:
        logger.error(f"User {message.from_user.id} not found")
        await message.answer(gettext("error_occurred"))
        return
    
    try:
        # Создаем VPN клиента
        email = f"user_{message.from_user.id}_{int(datetime.utcnow().timestamp())}@vpnbot"
        
        async with XUIService() as xui:
            client_data = await xui.create_client(email)
            
            if not client_data:
                # Уведомляем администратора об ошибке
                from app.config.settings import settings
                for admin_id in settings.ADMIN_IDS:
                    try:
                        await message.bot.send_message(
                            admin_id, 
                            f"Failed to create VPN client for user {message.from_user.id}"
                        )
                    except:
                        pass
                        
                await message.answer(gettext("vpn_creation_failed"))
                return
            
            # Генерируем ссылку для подключения
            connection_link = await xui.generate_vless_reality_link(
                client_data["uuid"], 
                client_data["email"]
            )
            
            # Сохраняем VPN клиента в БД
            vpn_repo = VPNClientRepository(message.db_session)
            vpn_client = await vpn_repo.create_vpn_client(
                user_id=user.id,
                uuid=client_data["uuid"],
                email=client_data["email"],
                inbound_id=xui.inbound_id,
                connection_link=connection_link  # В реальной реализации нужно шифровать
            )
            
            # Создаем подписку на 30 дней
            sub_repo = SubscriptionRepository(message.db_session)
            expire_at = datetime.utcnow() + timedelta(days=30)
            subscription = await sub_repo.create_subscription(
                vpn_client_id=vpn_client.id,
                expire_at=expire_at
            )
            
            # Создаем запись об оплате
            payment = await payment_repo.create_payment(
                telegram_payment_charge_id=telegram_payment_charge_id,
                stars_amount=message.successful_payment.total_amount,
                user_id=user.id,
                vpn_client_id=vpn_client.id
            )
            
            # Отправляем пользователю информацию о VPN
            await message.answer(
                gettext("vpn_created", link=connection_link),
                reply_markup=back_keyboard(gettext)
            )
            
    except Exception as e:
        logger.error(f"Error processing payment: {e}")
        await message.answer(gettext("vpn_creation_failed"))
