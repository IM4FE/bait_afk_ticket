from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime , Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    # Общие поля для всех таблиц (дата создания и обновления)
    created: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(32), nullable=True)
    full_name: Mapped[str] = mapped_column(String(128))

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_from: Mapped[int] = mapped_column(BigInteger)
    user_to: Mapped[int] = mapped_column(BigInteger)
    cause: Mapped[str] = mapped_column(String(128))
