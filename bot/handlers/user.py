from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter, Command
from aiogram.exceptions import TelegramForbiddenError
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext

from bot.states.ticket_form import TicketForm
from bot.database.requests import add_ticket, get_user, get_sender_tickets, get_receiver_tickets
from bot.keyboards.reply import cancel_kb, main_kb
from bot.keyboards.inline import throw_ticket_keyboard

user_router = Router()


@user_router.message(F.text == "Профиль", StateFilter(None))
async def cmd_profile(message: Message, session: AsyncSession):
    user = await get_user(session, message.from_user.id)
    if user is None:
        await message.answer('Сначала зарегистрируйтесь: /start')
        return
    
    await message.answer(f"Профиль\n" \
                        f"Имя: {user.full_name}\n" \
                        f"Юзернейм: @{user.username or '—'}\n" \
                        f"Отправлено тикетов: {len(await get_sender_tickets(session, message.from_user.id))}\n" \
                        f"Получено тикетов: {len(await get_receiver_tickets(session, message.from_user.id))}")


@user_router.message(F.text == "Отправить тикет", StateFilter(None))
async def cmd_submit_ticket(message: Message, state: FSMContext, session: AsyncSession):
    if await get_user(session, message.from_user.id) is None:
        await message.answer('Сначала зарегистрируйтесь: /start')
        return

    keyboard = await throw_ticket_keyboard(session, message.from_user.id)
    if not keyboard.inline_keyboard:
        await message.answer('Нет доступных пользователей для отправки тикета.')
        return
    await state.set_state(TicketForm.cause)
    await message.answer(
        "Кто забайтил?",
        reply_markup=keyboard
    )


@user_router.message(TicketForm.cause, F.text.startswith("/"))
@user_router.message(TicketForm.cause, F.text == "Отмена")
async def cancel_ticket_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Отправка тикета отменена.",
        reply_markup=main_kb()
    )


@user_router.callback_query(TicketForm.cause, F.data == "cancel_ticket_callback")
async def cancel_ticket_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Отправка тикета отменена.")
    await callback.message.delete()


@user_router.callback_query(TicketForm.cause, F.data.startswith("user:"))
async def process_ticket_user(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_id = callback.data.split(":")[1]
    user = await get_user(session, int(user_id))

    if user is None:
        await callback.answer("Пользователь не найден.")
        return
    
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Введите причину отправки тикета:", 
                                  reply_markup=cancel_kb())
    await state.update_data(user_to=user_id)


@user_router.message(TicketForm.cause, F.text, ~F.text.in_({"Профиль", "Отправить тикет", "Я даун"}))
async def process_ticket_cause(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    user_to_id = data.get("user_to")
    if user_to_id is None:
        await message.answer("Сначала выберите байтера: нажмите «Отправить тикет».")
        await state.clear()
        return
    user_to_id = int(user_to_id)
    cause = message.text

    await add_ticket(
        session, 
        message.from_user.id, 
        user_to_id, cause
        )
    await state.clear()

    user = await get_user(session, message.from_user.id)
    try:
        await message.bot.send_message(user_to_id, f"Вам тикет от {user.full_name}:\n{cause}")
    except TelegramForbiddenError:
        await message.answer("Тикет сохранён, но получатель заблокировал бота.")

    user = await get_user(session, user_to_id)
    if user is None:
        await message.answer(
            f"Тикет сохранён, но получатель (ID {user_to_id}) не найден в базе.",
            reply_markup=main_kb(),
        )
        return

    username = f"@{user.username}" if user.username else "без юзернейма"
    await message.answer(
        f"Тикет отправлен пользователю {user.full_name} ({username}) с причиной: {cause}",
        reply_markup=main_kb(),
    )


@user_router.message(F.text == "Я даун", StateFilter(None))
async def cmd_joke(message: Message, session: AsyncSession):
    user = await get_user(session, message.from_user.id)
    
    if user is None:
        await message.answer('Вы даун!')
        return
    
    await message.answer(f'{user.full_name}, вы даун!')


@user_router.message(TicketForm.cause)
async def cause_wrong_type(message: Message):
    await message.answer("Пришлите причину текстом.")