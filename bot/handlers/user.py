from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter, Command
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from bot.database.requests import get_user
from bot.keyboards.inline import throw_ticket_keyboard

user_router = Router()

@user_router.message(F.text == "Профиль", StateFilter(None))
async def cmd_profile(message: Message, session: AsyncSession):
    user = await get_user(session, message.from_user.id)
    if user is None:
        await message.answer('Сначала зарегистрируйтесь: /start')
        return
    
    await message.answer(f"Профиль\nИмя: {user.full_name}\nЮзернейм: @{user.username or '—'}")

@user_router.message(F.text == "Отправить тикет", StateFilter(None))
async def cmd_submit_ticket(message: Message, session: AsyncSession):
    if await get_user(session, message.from_user.id) is None:
        await message.answer('Сначала зарегистрируйтесь: /start')
        return
    
    await message.answer('Кто забайтил?',reply_markup=await throw_ticket_keyboard(session, message.from_user.id))  # Используем клавиатуру с пользователями

@user_router.callback_query(F.data.startswith("user:"))
async def process_ticket_user(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_id = callback.data.split(":")[1]
    user = await get_user(session, int(user_id))

    if user is None:
        await callback.answer("Пользователь не найден.")
        return
    
    await callback.answer()
    await callback.message.answer(f"Вы выбрали пользователя №{user_id}")
    await state.update_data(user_to=user_id)

@user_router.callback_query(F.data == "cancel_ticket")
async def cancel_ticket(callback: CallbackQuery):
    await callback.answer("Отправка тикета отменена.")
    await callback.message.delete()

@user_router.message(F.text == "Я даун")
async def cmd_joke(message: Message, session: AsyncSession):
    user = await get_user(session, message.from_user.id)
    
    if user is None:
        await message.answer('Вы даун!')
        return
    
    await message.answer(f'{user.full_name}, вы даун!')

@user_router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Вы отменили действие')