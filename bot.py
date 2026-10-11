import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from database import create_table
from handlers import routers


async def main():
    logging.basicConfig(level=logging.INFO)
    create_table()

    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(*routers)

    await bot.set_my_commands([
        BotCommand(command="start", description="Приветствие и помощь"),
        BotCommand(command="book", description="Забронировать столик"),
        BotCommand(command="mybookings", description="Мои брони"),
        BotCommand(command="cancel", description="Отменить бронирование"),
    ])

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
