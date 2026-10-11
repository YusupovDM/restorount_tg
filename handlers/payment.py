from aiogram import F, Router
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery

from config import DEPOSIT_RUB, DEPOSIT_STARS, PAYMENT_TOKEN
from database import cancel_booking, get_booking
from middlewares import PaymentMiddleware

router = Router()

# Мидлвер вешаем только на этот роутер: на pre_checkout и на сообщения об оплате
router.pre_checkout_query.middleware(PaymentMiddleware())
router.message.middleware(PaymentMiddleware())


@router.callback_query(F.data.startswith("pay:"))
async def send_invoice(callback: CallbackQuery):
    booking_id = int(callback.data.split(":")[1])
    booking = get_booking(booking_id)

    if not booking or booking["user_id"] != callback.from_user.id:
        await callback.answer("Бронь не найдена", show_alert=True)
        return
    if booking["status"] != "awaiting_payment":
        await callback.answer("Эта бронь не требует оплаты", show_alert=True)
        return

    if PAYMENT_TOKEN:          # оплата через провайдера (ЮKassa и т.п.), сумма в копейках
        currency, amount = "RUB", DEPOSIT_RUB * 100
    else:                      # Telegram Stars
        currency, amount = "XTR", DEPOSIT_STARS

    await callback.message.answer_invoice(
        title=f"Депозит за бронь #{booking_id}",
        description=f"{booking['date']} в {booking['time']}, гостей: {booking['guests']}",
        payload=f"booking:{booking_id}",
        provider_token=PAYMENT_TOKEN,
        currency=currency,
        prices=[LabeledPrice(label="Депозит", amount=amount)],
    )
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery, booking: dict):
    # Все проверки уже сделал PaymentMiddleware — сюда доходят только валидные платежи
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, booking: dict):
    # Бронь уже зафиксирована в БД мидлвером
    await message.answer(
        f"🎉 Оплата прошла! Бронь #{booking['id']} подтверждена.\n"
        f"📅 {booking['date']} в {booking['time']}, гостей: {booking['guests']}.\n\n"
        "Ваши брони: /mybookings"
    )


@router.callback_query(F.data.startswith("cancel:"))
async def cancel_booking_cb(callback: CallbackQuery):
    booking_id = int(callback.data.split(":")[1])
    booking = get_booking(booking_id)

    if cancel_booking(booking_id, callback.from_user.id):
        text = f"❌ Бронь #{booking_id} отменена."
        if booking["payment_status"] == "paid":
            text += "\nПо возврату депозита с вами свяжется администратор."
        await callback.message.edit_text(text)
        await callback.answer("Бронь отменена")
    else:
        await callback.answer("Бронь не найдена или уже отменена", show_alert=True)
