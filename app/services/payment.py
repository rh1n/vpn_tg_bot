# app/services/payment.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Payment, PaymentStatus
from app.config.settings import settings
from app.utils.logger import logger

class PaymentService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_payment(
        self, 
        telegram_payment_charge_id: str, 
        stars_amount: int, 
        user_id: int
    ) -> Payment:
        """Создание записи об оплате"""
        try:
            payment = Payment(
                telegram_payment_charge_id=telegram_payment_charge_id,
                stars_amount=stars_amount,
                user_id=user_id,
                status=PaymentStatus.PENDING
            )
            self.db_session.add(payment)
            await self.db_session.flush()
            return payment
        except Exception as e:
            logger.error(f"Error creating payment record: {e}")
            raise

    async def update_payment_status(
        self, 
        telegram_payment_charge_id: str, 
        status: PaymentStatus
    ) -> bool:
        """Обновление статуса оплаты"""
        try:
            result = await self.db_session.execute(
                Payment.__table__.update()
                .where(Payment.telegram_payment_charge_id == telegram_payment_charge_id)
                .values(status=status)
            )
            await self.db_session.commit()
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating payment status: {e}")
            await self.db_session.rollback()
            return False

    async def is_payment_exists(self, telegram_payment_charge_id: str) -> bool:
        """Проверка существования оплаты"""
        try:
            result = await self.db_session.execute(
                Payment.__table__.select()
                .where(Payment.telegram_payment_charge_id == telegram_payment_charge_id)
            )
            return result.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking payment existence: {e}")
            return False
