from datetime import date, timedelta

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from config import BOOKING_DAYS, CLOSE_HOUR, MAX_GUESTS, OPEN_HOUR


def _rows(items, per_row):
    buttons = [KeyboardButton(text=item) for item in items]
    return [buttons[i:i + per_row] for i in range(0, len(buttons), per_row)]


# ---------- Reply-кнопки ----------

def dates_kb():
    days = [(date.today() + timedelta(days=i)).strftime("%d.%m.%Y") for i in range(BOOKING_DAYS)]
    return ReplyKeyboardMarkup(keyboard=_rows(days, 3), resize_keyboard=True)


def times_kb():
    times = [f"{h}:00" for h in range(OPEN_HOUR, CLOSE_HOUR + 1)]
    return ReplyKeyboardMarkup(
        keyboard=_rows(times, 4),
        resize_keyboard=True,
        input_field_placeholder="Например, 18:00",
    )


def guests_kb():
    guests = [str(i) for i in range(1, MAX_GUESTS + 1)]
    return ReplyKeyboardMarkup(keyboard=_rows(guests, 5), resize_keyboard=True)


def yes_no_kb():
    return ReplyKeyboardMarkup(keyboard=_rows(["Да", "Нет"], 2), resize_keyboard=True)


# ---------- Inline-кнопки ----------

def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="abort"),
    ]])


def pay_kb(booking_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="💳 Оплатить депозит", callback_data=f"pay:{booking_id}"),
    ]])


def booking_kb(booking):
    rows = []
    if booking["status"] == "awaiting_payment":
        rows.append([InlineKeyboardButton(text="💳 Оплатить депозит", callback_data=f"pay:{booking['id']}")])
    rows.append([
        # switch_inline_query открывает выбор чата и подставляет "@бот <id>" -> Inline Mode
        InlineKeyboardButton(text="📤 Поделиться", switch_inline_query=str(booking["id"])),
        InlineKeyboardButton(text="🗑 Отменить", callback_data=f"cancel:{booking['id']}"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)
