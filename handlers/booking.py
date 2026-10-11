from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from config import CLOSE_HOUR, MAX_GUESTS, OPEN_HOUR
from database import add_booking, is_slot_available
from filters import DateFilter, GuestsFilter, TimeFilter
from keyboards import confirm_kb, dates_kb, guests_kb, pay_kb, times_kb, yes_no_kb
from states import Booking
from texts import deposit_required, deposit_text, summary_text

router = Router()


@router.message(Command("book"))
async def cmd_book(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Booking.date)
    await message.answer("📅 Выберите дату для бронирования.", reply_markup=dates_kb())


# ---------- Шаг 1: дата ----------

@router.message(Booking.date, DateFilter())
async def process_date(message: Message, state: FSMContext, booking_date: str):
    await state.update_data(date=booking_date)
    await state.set_state(Booking.time)
    await message.answer("🕐 Введите время (например, 18:00).", reply_markup=times_kb())


@router.message(Booking.date)
async def wrong_date(message: Message):
    await message.answer("Выберите дату кнопкой ниже (формат ДД.ММ.ГГГГ).", reply_markup=dates_kb())


# ---------- Шаг 2: время ----------

@router.message(Booking.time, TimeFilter())
async def process_time(message: Message, state: FSMContext, booking_time: str):
    await state.update_data(time=booking_time)
    await state.set_state(Booking.guests)
    await message.answer("👥 Сколько человек будет на бронировании?", reply_markup=guests_kb())


@router.message(Booking.time)
async def wrong_time(message: Message):
    await message.answer(
        f"Некорректное время. Мы принимаем брони с {OPEN_HOUR}:00 до {CLOSE_HOUR}:00, "
        "формат ЧЧ:ММ, и время не должно быть в прошлом.",
        reply_markup=times_kb(),
    )


# ---------- Шаг 3: количество гостей ----------

@router.message(Booking.guests, GuestsFilter())
async def process_guests(message: Message, state: FSMContext, guests: int):
    await state.update_data(guests=guests)
    await state.set_state(Booking.window)
    await message.answer("🪟 Хотите выбрать место около окна?", reply_markup=yes_no_kb())


@router.message(Booking.guests)
async def wrong_guests(message: Message):
    await message.answer(f"Введите число от 1 до {MAX_GUESTS}.", reply_markup=guests_kb())


# ---------- Шаг 4: предпочтение по месту ----------

@router.message(Booking.window, F.text.in_({"Да", "Нет"}))
async def process_window(message: Message, state: FSMContext):
    near_window = message.text == "Да"
    data = await state.get_data()

    if not is_slot_available(data["date"], data["time"], near_window):
        await state.set_state(Booking.time)
        place = "у окна" if near_window else "в зале"
        await message.answer(
            f"😔 На {data['date']} в {data['time']} свободных столиков {place} нет.\n"
            "Выберите другое время.",
            reply_markup=times_kb(),
        )
        return

    await state.update_data(near_window=near_window)
    await state.set_state(Booking.confirm)
    data = await state.get_data()

    await message.answer("Почти готово!", reply_markup=ReplyKeyboardRemove())
    await message.answer(summary_text(data), reply_markup=confirm_kb())


@router.message(Booking.window)
async def wrong_window(message: Message):
    await message.answer("Ответьте «Да» или «Нет».", reply_markup=yes_no_kb())


# ---------- Шаг 5: подтверждение (inline-кнопки) ----------

@router.callback_query(Booking.confirm, F.data == "confirm")
async def confirm_booking(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    # Повторная проверка: пока пользователь думал, столик могли занять
    if not is_slot_available(data["date"], data["time"], data["near_window"]):
        await state.clear()
        await callback.message.edit_text("😔 Это время только что заняли. Попробуйте ещё раз: /book")
        await callback.answer()
        return

    if deposit_required(data["guests"]):
        booking_id = add_booking(
            callback.from_user.id, data["date"], data["time"], data["guests"],
            data["near_window"], status="awaiting_payment", payment_status="pending",
        )
        await callback.message.edit_text(
            f"{summary_text(data)}\n\n"
            f"📝 Бронь #{booking_id} создана. Для подтверждения брони требуется депозит "
            f"{deposit_text()}. Пожалуйста, внесите оплату.",
            reply_markup=pay_kb(booking_id),
        )
    else:
        booking_id = add_booking(
            callback.from_user.id, data["date"], data["time"], data["guests"],
            data["near_window"], status="confirmed", payment_status="not_required",
        )
        await callback.message.edit_text(
            f"{summary_text(data)}\n\n✅ Бронь #{booking_id} подтверждена! Ждём вас.\n"
            "Ваши брони: /mybookings"
        )

    await state.clear()
    await callback.answer()


@router.callback_query(Booking.confirm, F.data == "abort")
async def abort_booking(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Бронирование отменено. Начать заново: /book")
    await callback.answer()
