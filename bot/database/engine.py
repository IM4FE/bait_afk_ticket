from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from bot.config import config
from bot.database.models import Base

# Создаем асинхронный движок (например, для SQLite или PostgreSQL)
# URL берется из конфига: "sqlite+aiosqlite:///db.sqlite3" или "postgresql+asyncpg://user:pass@localhost/dbname"
engine = create_async_engine(url=config.db_url.get_secret_value(), echo=False)

# Фабрика сессий. expire_on_commit=False обязателен для асинхронной работы
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def create_db() -> None:
    """Создает все таблицы, описанные в моделях."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """Удаляет все таблицы (полезно при тестировании)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)