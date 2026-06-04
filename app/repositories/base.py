# app/repositories/base.py
from typing import Optional, List, TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import User, VPNClient, Subscription, Payment

T = TypeVar('T')

class BaseRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

class UserRepository(BaseRepository):
    async def create_or_update_user(
        self, 
        telegram_id: int, 
        username: Optional[str] = None, 
        language_code: str = "ru"
    ) -> User:
        """Создание или обновление пользователя"""
        result = await self.db_session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Обновляем существующего пользователя
            user.username = username
            user.language_code = language_code
        else:
            # Создаем нового пользователя
            user = User(
                telegram_id=telegram_id,
                username=username,
                language_code=language_code
            )
            self.db_session.add(user)
            
        await self.db_session.flush()
        return user

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получение пользователя по Telegram ID"""
        result = await self.db_session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

class VPNClientRepository(BaseRepository):
    async def create_vpn_client(
        self, 
        user_id: int, 
        uuid: str, 
        email: str, 
        inbound_id: int, 
        connection_link: str
    ) -> VPNClient:
        """Создание VPN клиента"""
        vpn_client = VPNClient(
            user_id=user_id,
            uuid=uuid,
            email=email,
            inbound_id=inbound_id,
            connection_link=connection_link
        )
        self.db_session.add(vpn_client)
        await self.db_session.flush()
        return vpn_client

    async def get_vpn_client_by_id(self, client_id: int) -> Optional[VPNClient]:
        """Получение VPN клиента по ID"""
        result = await self.db_session.execute(
            select(VPNClient).where(VPNClient.id == client_id)
        )
        return result.scalar_one_or_none()

    async def get_vpn_clients_by_user_id(self, user_id: int) -> List[VPNClient]:
        """Получение всех VPN клиентов пользователя"""
        result = await self.db_session.execute(
            select(VPNClient).where(VPNClient.user_id == user_id)
        )
        return result.scalars().all()

    async def delete_vpn_client(self, client_id: int) -> bool:
        """Удаление VPN клиента"""
        result = await self.db_session.execute(
            VPNClient.__table__.delete().where(VPNClient.id == client_id)
        )
        await self.db_session.commit()
        return result.rowcount > 0

class SubscriptionRepository(BaseRepository):
    async def create_subscription(
        self, 
        vpn_client_id: int, 
        expire_at
    ) -> Subscription:
        """Создание подписки"""
        subscription = Subscription(
            vpn_client_id=vpn_client_id,
            expire_at=expire_at
        )
        self.db_session.add(subscription)
        await self.db_session.flush()
        return subscription

    async def get_active_subscriptions(self) -> List[Subscription]:
        """Получение активных подписок"""
        from sqlalchemy import and_
        from app.database.models import SubscriptionStatus
        from datetime import datetime
        
        result = await self.db_session.execute(
            select(Subscription).where(
                and_(
                    Subscription.status == SubscriptionStatus.ACTIVE,
                    Subscription.expire_at > datetime.utcnow()
                )
            )
        )
        return result.scalars().all()

    async def get_expiring_subscriptions(self, days: int) -> List[Subscription]:
        """Получение подписок, истекающих через указанное количество дней"""
        from sqlalchemy import and_, func
        from app.database.models import SubscriptionStatus
        from datetime import datetime, timedelta
        
        target_date = datetime.utcnow() + timedelta(days=days)
        
        result = await self.db_session.execute(
            select(Subscription).where(
                and_(
                    Subscription.status == SubscriptionStatus.ACTIVE,
                    func.date(Subscription.expire_at) == target_date.date()
                )
            )
        )
        return result.scalars().all()

    async def renew_subscription(self, subscription_id: int, new_expire_at) -> bool:
        """Продление подписки"""
        try:
            result = await self.db_session.execute(
                Subscription.__table__.update()
                .where(Subscription.id == subscription_id)
                .values(expire_at=new_expire_at)
            )
            await self.db_session.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db_session.rollback()
            raise

class PaymentRepository(BaseRepository):
    async def create_payment(
        self, 
        telegram_payment_charge_id: str, 
        stars_amount: int, 
        user_id: int,
        vpn_client_id: Optional[int] = None
    ) -> Payment:
        """Создание записи об оплате"""
        from app.database.models import PaymentStatus
        
        payment = Payment(
            telegram_payment_charge_id=telegram_payment_charge_id,
            stars_amount=stars_amount,
            user_id=user_id,
            vpn_client_id=vpn_client_id,
            status=PaymentStatus.SUCCESS
        )
        self.db_session.add(payment)
        await self.db_session.flush()
        return payment

    async def is_payment_exists(self, telegram_payment_charge_id: str) -> bool:
        """Проверка существования оплаты"""
        result = await self.db_session.execute(
            select(Payment).where(Payment.telegram_payment_charge_id == telegram_payment_charge_id)
        )
        return result.scalar_one_or_none() is not None
