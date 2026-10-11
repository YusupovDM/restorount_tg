from datetime import date, datetime, timedelta

from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import BOOKING_DAYS, CLOSE_HOUR, MAX_GUESTS, OPEN_HOUR


class DateFilter(BaseFilter):
    """Дата в формате ДД.ММ.ГГГГ, от сегодня до +BOOKING_DAYS дней."""

    async def __call__(self, message: Message):
        try:
            d = datetime.strptime(message.text or "", "%d.%m.%Y").date()
        except ValueError:
            return False

        today = date.today()
        if today <= d < today + timedelta(days=BOOKING_DAYS):
            # Словарь из фильтра попадает в аргументы хендлера
            return {"booking_date": d.strftime("%d.%m.%Y")}
        return False


class TimeFilter(BaseFilter):
    """Время ЧЧ:ММ в часы работы. Если бронь на сегодня — время ещё не прошло."""

    async def __call__(self, message: Message, state: FSMContext):
        try:
            t = datetime.strptime(message.text or "", "%H:%M").time()
        except ValueError:
            return False

        if not (OPEN_HOUR <= t.hour <= CLOSE_HOUR):
            return False
        if t.hour == CLOSE_HOUR and t.minute > 0:
            return False

        data = await state.get_data()
        booking_day = datetime.strptime(data["date"], "%d.%m.%Y").date()
        if booking_day == date.today() and t <= datetime.now().time():
            return False

        return {"booking_time": t.strftime("%H:%M")}


class GuestsFilter(BaseFilter):
    """Количество гостей — целое число от 1 до MAX_GUESTS."""

    async def __call__(self, message: Message):
        text = message.text or ""
        if text.isdigit() and 1 <= int(text) <= MAX_GUESTS:
            return {"guests": int(text)}
        return False
