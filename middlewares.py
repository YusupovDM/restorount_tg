from aiogram import BaseMiddleware
from aiogram.types import Message, PreCheckoutQuery

from database import get_booking, is_slot_available, mark_paid


def booking_id_from_payload(payload):
    # payload вида "booking:15"
    return int(payload.split(":")[1])


class PaymentMiddleware(BaseMiddleware):
    """
    1) PreCheckoutQuery — перед списанием денег проверяем, что бронь существует
       и время всё ещё свободно. Если нет — отклоняем платёж.
    2) SuccessfulPayment — фиксируем оплату и бронь в базе данных.
    Найденная бронь передаётся в хендлер через data["booking"].
    """

    async def __call__(self, handler, event, data):
        if isinstance(event, PreCheckoutQuery):
            booking = get_booking(booking_id_from_payload(event.invoice_payload))

            if not booking or booking["status"] != "awaiting_payment":
                await event.answer(ok=False, error_message="Бронь не найдена или уже оплачена.")
                return

            if not is_slot_available(booking["date"], booking["time"], booking["near_window"]):
                await event.answer(
                    ok=False,
                    error_message="Увы, это время уже заняли. Оформите бронь на другое время.",
                )
                return

            data["booking"] = booking

        elif isinstance(event, Message) and event.successful_payment:
            booking_id = booking_id_from_payload(event.successful_payment.invoice_payload)
            mark_paid(booking_id)
            data["booking"] = get_booking(booking_id)

        return await handler(event, data)
