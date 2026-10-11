from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from database import get_user_bookings
from keyboards import booking_kb
from texts import booking_text

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"👋 Здравствуйте, {message.from_user.first_name}!\n\n"
        "Я помогу забронировать столик в нашем ресторане.\n\n"
        "/book — забронировать столик\n"
        "/mybookings — мои брони\n"
        "/cancel — отменить бронирование\n\n"
        "Поделиться бронью можно в любом чате: напишите <code>@имя_бота</code> "
        "и выберите бронь из списка.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(Command("mybookings"))
async def cmd_my_bookings(message: Message):
    bookings = get_user_bookings(message.from_user.id)
    if not bookings:
        await message.answer("У вас нет активных броней. Забронировать: /book")
        return

    for b in bookings:
        await message.answer(booking_text(b), reply_markup=booking_kb(b))


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    # Если пользователь в процессе бронирования — прерываем FSM
    if await state.get_state() is not None:
        await state.clear()
        await message.answer("Бронирование прервано.", reply_markup=ReplyKeyboardRemove())
        return

    # Иначе — показываем активные брони с кнопкой отмены
    bookings = get_user_bookings(message.from_user.id)
    if not bookings:
        await message.answer("Отменять нечего — активных броней нет.")
        return

    await message.answer("Какую бронь отменить?")
    for b in bookings:
        await message.answer(booking_text(b), reply_markup=booking_kb(b))
