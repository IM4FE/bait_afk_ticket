from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states.registration import Registration
from bot.database.requests import add_user, get_user
from bot.keyboards.reply import main_kb, cancel_kb

registration_router = Router()

MAX_NAME_LEN = 128  # как в модели: String(128)


@registration_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()  # начинаем с чистого листа

    user = await get_user(session, message.from_user.id)
    if user is not None:
        await message.answer(
            f"С возвращением, {user.full_name}!",
            reply_markup=main_kb(),
        )
        return

    await state.set_state(Registration.full_name)
    await message.answer(
        "Привет! Давайте познакомимся.\n"
        "Введите ваше имя и фамилию (например: Иван Петров):",
        reply_markup=cancel_kb(),
    )


@registration_router.message(Registration.full_name, F.text == "Отмена")
@registration_router.message(Registration.full_name, F.text.startswith("/"))
async def cancel_registration(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Регистрация отменена. Начать заново — /start",
        reply_markup=ReplyKeyboardRemove(),
    )


@registration_router.message(Registration.full_name, ~F.text.in_({"Профиль", "Отправить тикет", "Я даун"}))
async def process_full_name(message: Message, state: FSMContext, session: AsyncSession):
    full_name = " ".join(message.text.split())  # схлопываем пробелы

    if len(full_name) < 2:
        await message.answer("Слишком короткое имя. Введите имя и фамилию:")
        return
    if len(full_name) > MAX_NAME_LEN:
        await message.answer(f"Максимум {MAX_NAME_LEN} символов. Сократите, пожалуйста:")
        return

    await add_user(
        session,
        tg_id=message.from_user.id,
        full_name=full_name,
        username=message.from_user.username,
    )
    await state.clear()

    await message.answer(
        f"Отлично, {full_name}! Регистрация завершена.",
        reply_markup=main_kb(),
    )

@registration_router.message(Registration.full_name)
async def process_full_name_invalid(message: Message):
    await message.answer(
        "Пожалуйста, введите ваше имя и фамилию (например: Иван Петров):"
    )

@registration_router.message(Registration.full_name)
async def process_invalid_message(message: Message):
    await message.answer(
        "Не понял. /start для начала регистрации."
    )