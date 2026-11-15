from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.database.requests import get_users
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models import User

async def throw_ticket_keyboard(session: AsyncSession, current_user: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    users = await get_users(session)  # Получаем список пользователей из базы данных

    if len(users) <= 1:
        return keyboard  # Возвращаем пустую клавиатуру, если пользователей нет
    
    for user in users:
        if user.tg_id != current_user:
            button = InlineKeyboardButton(text=f"{user.full_name} ({user.username})", callback_data=f"user:{user.tg_id}")  # Создаем кнопку для каждого пользователя
            keyboard.inline_keyboard.append([button])  # Добавляем кнопку в клавиатуру
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="Отмена", callback_data="cancel_ticket_callback")])  # Добавляем кнопку "Отмена"
    return keyboard
