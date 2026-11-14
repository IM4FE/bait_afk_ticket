from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models import User, Ticket


async def add_user(session: AsyncSession, tg_id: int, full_name: str, username: str | None = None) -> None:
    """Добавляет пользователя, если его еще нет в базе."""
    query = select(User).where(User.tg_id == tg_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        new_user = User(
            tg_id=tg_id,
            full_name=full_name,
            username=username
        )
        session.add(new_user)
        await session.commit()
    elif user.username != username:
        user.full_name = full_name
        user.username = username
        await session.commit()

async def get_user(session: AsyncSession, tg_id: int) -> User | None:
    """Возвращает объект пользователя по его Telegram ID."""
    query = select(User).where(User.tg_id == tg_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def get_users(session: AsyncSession) -> list[User] | None:
    """Возвращает список пользователей."""
    query = select(User)
    result = await session.execute(query)
    return list(result.scalars().all())

async def get_sender_tickets(session: AsyncSession, tg_id: int) -> list[Ticket] | None:
    """Возвращает список тикетов у пользователя как отправителя."""
    query = select(Ticket).where(Ticket.user_from == tg_id)
    result = await session.execute(query)
    return list(result.scalars().all())

async def get_receiver_tickets(session: AsyncSession, tg_id: int) -> list[Ticket] | None:
    """Возвращает список тикетов у пользователя как получателя."""
    query = select(Ticket).where(Ticket.user_to == tg_id)
    result = await session.execute(query)
    return list(result.scalars().all())