# app/scheduler/tasks.py
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import SubscriptionRepository
from app.services.xui import XUIService
from app.services.notification import NotificationService
from app.database.models import SubscriptionStatus
from app.utils.logger import logger

async def check_expired_subscriptions(db_session: AsyncSession, bot) -> None:
    """Проверка истекших подписок"""
    try:
        sub_repo = SubscriptionRepository(db_session)
        
        # Получаем истекшие активные подписки
        result = await db_session.execute(
            "SELECT s.id, s.vpn_client_id, vc.user_id, vc.uuid "
            "FROM subscriptions s "
            "JOIN vpn_clients vc ON s.vpn_client_id = vc.id "
            "WHERE s.status = 'active' AND s.expire_at < :now",
            {"now": datetime.utcnow()}
        )
        expired_subs = result.fetchall()
        
        if not expired_subs:
            return
            
        async with XUIService() as xui:
            notification_service = NotificationService(bot, db_session)
            
            for sub in expired_subs:
                try:
                    # Отключаем клиента в панели
                    await xui.delete_client(str(sub.uuid))
                    
                    # Обновляем статус подписки
                    await db_session.execute(
                        "UPDATE subscriptions SET status = 'expired' WHERE id = :id",
                        {"id": sub.id}
                    )
                    
                    # Уведомляем пользователя
                    await notification_service.send_message_to_user(
                        sub.user_id,
                        "Ваша VPN подписка истекла. Для продолжения использования купите новую подписку."
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing expired subscription {sub.id}: {e}")
                    continue
            
            await db_session.commit()
            
    except Exception as e:
        logger.error(f"Error in check_expired_subscriptions: {e}")
        await db_session.rollback()

async def send_expiration_notifications(db_session: AsyncSession, bot, days: int) -> None:
    """Отправка уведомлений об истечении подписки"""
    try:
        sub_repo = SubscriptionRepository(db_session)
        subscriptions = await sub_repo.get_expiring_subscriptions(days)
        
        if not subscriptions:
            return
            
        notification_service = NotificationService(bot, db_session)
        
        for subscription in subscriptions:
            try:
                # Получаем информацию о пользователе
                result = await db_session.execute(
                    "SELECT vc.user_id FROM vpn_clients vc WHERE vc.id = :client_id",
                    {"client_id": subscription.vpn_client_id}
                )
                user_info = result.fetchone()
                
                if user_info:
                    message = f"Ваша VPN подписка истекает через {days} дней. Продлите подписку, чтобы сохранить доступ."
                    await notification_service.send_message_to_user(user_info.user_id, message)
                    
            except Exception as e:
                logger.error(f"Error sending expiration notification: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error in send_expiration_notifications: {e}")
