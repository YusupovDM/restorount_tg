from aiogram.fsm.state import State, StatesGroup


class Booking(StatesGroup):
    date = State()
    time = State()
    guests = State()
    window = State()
    confirm = State()
