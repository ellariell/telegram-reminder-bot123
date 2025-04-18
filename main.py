
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8024512141:AAEh9FqWUog1zOSMhwK-FNIxheKViLGfJRM")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задано. Убедитесь, что токен задан в переменных окружения или в коде.")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привет! Я жив и работаю 🟢")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
