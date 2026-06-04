# app/database/models.py
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, 
    Boolean, Text, Enum as SQLEnum, UniqueConstraint
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import enum
import uuid

Base = declarative_base()

class UserLanguage(enum.Enum):
    RU = "ru"
    EN = "en"

class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"

class PaymentStatus(enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    language_code = Column(SQLEnum(UserLanguage), default=UserLanguage.RU)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id})>"

class VPNClient(Base):
    __tablename__ = "vpn_clients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    inbound_id = Column(Integer, nullable=False)
    connection_link = Column(Text, nullable=False)  # Зашифрованная ссылка
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<VPNClient(id={self.id}, email={self.email})>"

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    vpn_client_id = Column(Integer, ForeignKey("vpn_clients.id"), nullable=False)
    expire_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, status={self.status})>"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_payment_charge_id = Column(String, unique=True, nullable=False)
    stars_amount = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vpn_client_id = Column(Integer, ForeignKey("vpn_clients.id"), nullable=True)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.stars_amount})>"
