# 🍽 Бот для бронирования столиков в ресторане (MVP)

Учебный проект ANSAR.SCHOOL на **aiogram 3.x**: команды, фильтры, FSM, мидлвер,
reply/inline-кнопки, Inline Mode, оплата депозита, SQLite и деплой в Docker.

## Структура

```
restaurant_bot/
├── bot.py              # точка входа: Bot, Dispatcher, роутеры, команды меню
├── config.py           # настройки (.env + параметры ресторана)
├── database.py         # SQLite: create_table / add_booking / get_booking / cancel_booking / ...
├── states.py           # FSM: date -> time -> guests -> window -> confirm
├── filters.py          # DateFilter, TimeFilter, GuestsFilter (проверка ввода)
├── middlewares.py      # PaymentMiddleware: проверка времени перед оплатой + фиксация в БД
├── keyboards.py        # reply- и inline-клавиатуры
├── texts.py            # форматирование сообщений
├── handlers/
│   ├── start.py        # /start, /mybookings, /cancel
│   ├── booking.py      # /book и все шаги FSM
│   ├── payment.py      # счёт, pre_checkout, успешная оплата, отмена брони
│   └── inline.py       # Inline Mode — поделиться бронью
├── Dockerfile
└── docker-compose.yml
```

## Что умеет

| Тема слайда | Где в коде |
|---|---|
| `/start`, `/book`, `/mybookings`, `/cancel` | `handlers/start.py`, `handlers/booking.py` |
| FSM: дата → время → гости → окно | `states.py`, `handlers/booking.py` |
| Фильтры (дата, время, кол-во гостей) | `filters.py` — фильтр возвращает `dict`, и значение приходит аргументом в хендлер |
| Мидлвер оплаты | `middlewares.py` — перед списанием проверяет, что столик свободен; после оплаты помечает бронь оплаченной |
| Reply-кнопки (дата, время, гости, Да/Нет) | `keyboards.py` |
| Inline-кнопки (подтвердить, оплатить, отменить, поделиться) | `keyboards.py` |
| Inline Mode | `handlers/inline.py` — в любом чате `@имя_бота` → выбрать бронь |
| Оплата депозита | `handlers/payment.py` — Telegram Stars или провайдер (ЮKassa) |
| SQLite | `database.py`, таблица `bookings` |
| Деплой | `Dockerfile`, `docker-compose.yml` |

**Логика ресторана** (`config.py`): 10 столиков, из них 3 у окна; брони с 12:00 до 22:00 на 7 дней вперёд;
депозит обязателен от 4 гостей. Занятость считается по точному слоту «дата + время» —
для MVP этого достаточно. Слот занимают только подтверждённые брони
(без депозита — сразу, с депозитом — после оплаты).

## Запуск локально

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # впишите BOT_TOKEN
python bot.py
```

### Настройка в @BotFather

1. **Inline Mode:** `/setinline` → выбрать бота → ввести подсказку, например «Выберите бронь».
2. **Оплата:**
   - по умолчанию (`PAYMENT_TOKEN` пустой) — **Telegram Stars**, ничего настраивать не нужно;
   - для рублей: `/mybots` → бот → **Payments** → провайдер (например, ЮKassa Test) →
     скопировать токен в `PAYMENT_TOKEN`. Тестовая карта ЮKassa: `5555 5555 5555 4444`, любая дата и CVC.

## Деплой на сервер (VPS)

```bash
git clone <repo> && cd restaurant_bot
cp .env.example .env && nano .env
docker compose up -d --build
docker compose logs -f
```

База лежит в `./data/bookings.db` и переживает перезапуск контейнера.
Без Docker бота можно запустить на PythonAnywhere (Always-on task: `python bot.py`).

## Как проверить сценарий

1. `/book` → дата → `18:00` → `2` → «Да» → «✅ Подтвердить» — бронь подтверждена без депозита.
2. `/book` → … → `5` гостей → «Подтвердить» → «💳 Оплатить депозит» → оплатить счёт.
3. `/mybookings` → «📤 Поделиться» → выбрать чат → выбрать бронь из inline-списка.
4. `/cancel` во время заполнения прерывает FSM, вне FSM — показывает брони для отмены.
5. Введите `25:00` или `0` гостей — сработают фильтры.

## Идеи для развития

- Учитывать длительность визита (столик занят 2 часа), а не точный слот
- Снимать неоплаченные брони через N минут
- Панель администратора: список броней на день, уведомления в чат ресторана
- Хранить FSM в Redis вместо MemoryStorage
