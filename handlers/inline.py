from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from database import get_user_bookings
from texts import share_text

router = Router()


@router.inline_query()
async def share_booking(query: InlineQuery):
    bookings = [b for b in get_user_bookings(query.from_user.id) if b["status"] == "confirmed"]

    # "@бот 15" — показать только бронь #15
    if query.query.strip().isdigit():
        bookings = [b for b in bookings if b["id"] == int(query.query.strip())]

    results = [
        InlineQueryResultArticle(
            id=str(b["id"]),
            title=f"Бронь #{b['id']} — {b['date']} в {b['time']}",
            description=f"Гостей: {b['guests']}, " + ("у окна" if b["near_window"] else "в зале"),
            input_message_content=InputTextMessageContent(message_text=share_text(b), parse_mode="HTML"),
        )
        for b in bookings
    ]

    # is_personal — у каждого пользователя свои результаты
    await query.answer(results, cache_time=1, is_personal=True)
