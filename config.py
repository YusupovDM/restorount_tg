import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Путь к базе SQLite (в Docker переопределяется через переменную окружения)
DB_PATH = os.getenv("DB_PATH", "bookings.db")

# --- Оплата ---
# Пустой PAYMENT_TOKEN -> оплата в Telegram Stars (XTR), токен провайдера не нужен.
# Токен от ЮKassa/другого провайдера (BotFather -> Payments) -> оплата в рублях.
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN", "")
DEPOSIT_RUB = int(os.getenv("DEPOSIT_RUB", "500"))
DEPOSIT_STARS = int(os.getenv("DEPOSIT_STARS", "50"))
# Депозит требуется, если гостей >= этого числа (условие ресторана)
DEPOSIT_FROM_GUESTS = int(os.getenv("DEPOSIT_FROM_GUESTS", "4"))

# --- Ресторан ---
TOTAL_TABLES = 10   # всего столиков
WINDOW_TABLES = 3   # из них у окна
OPEN_HOUR = 12      # первое время брони 12:00
CLOSE_HOUR = 22     # последнее время брони 22:00
MAX_GUESTS = 10
BOOKING_DAYS = 7    # на сколько дней вперёд можно бронировать
