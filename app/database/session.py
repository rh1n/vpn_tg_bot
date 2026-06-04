# app/database/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

# Создаем асинхронный движок
engine = create_async_engine(
    settings.POSTGRES_DSN,
    echo=False,  # Установите True для отладки SQL запросов
    pool_pre_ping=True,
    pool_recycle=300,
)

# Создаем фабрику сессий
async_session_maker = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_session() -> AsyncSession:
    """Dependency для получения сессии БД"""
    async with async_session_maker() as session:
        yield session
