from config import DEPOSIT_FROM_GUESTS, DEPOSIT_RUB, DEPOSIT_STARS, PAYMENT_TOKEN

STATUS_TEXT = {
    "awaiting_payment": "⏳ ожидает оплаты депозита",
    "confirmed": "✅ подтверждена",
    "cancelled": "❌ отменена",
}

PAYMENT_TEXT = {
    "not_required": "не требуется",
    "pending": "не оплачен",
    "paid": "оплачен",
}


def deposit_required(guests):
    return guests >= DEPOSIT_FROM_GUESTS


def deposit_text():
    return f"{DEPOSIT_RUB} ₽" if PAYMENT_TOKEN else f"{DEPOSIT_STARS} ⭐"


def summary_text(data):
    place = "у окна" if data["near_window"] else "в зале"
    text = (
        "<b>Проверьте бронь:</b>\n\n"
        f"📅 Дата: {data['date']}\n"
        f"🕐 Время: {data['time']}\n"
        f"👥 Гостей: {data['guests']}\n"
        f"🪑 Место: {place}\n"
    )
    if deposit_required(data["guests"]):
        text += f"\n💳 Для подтверждения требуется депозит: {deposit_text()}"
    return text.rstrip()


def booking_text(b):
    place = "у окна" if b["near_window"] else "в зале"
    return (
        f"<b>Бронь #{b['id']}</b>\n"
        f"📅 {b['date']}  🕐 {b['time']}\n"
        f"👥 Гостей: {b['guests']}, место: {place}\n"
        f"Статус: {STATUS_TEXT[b['status']]}\n"
        f"Депозит: {PAYMENT_TEXT[b['payment_status']]}"
    )


def share_text(b):
    place = "у окна" if b["near_window"] else "в зале"
    return (
        "🍽 <b>Я забронировал столик!</b>\n\n"
        f"📅 {b['date']} в {b['time']}\n"
        f"👥 Гостей: {b['guests']}\n"
        f"🪑 Место: {place}\n\n"
        "Ждём вас 😉"
    )
