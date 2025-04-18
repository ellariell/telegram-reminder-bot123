
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set. Убедитесь, что токен задан в переменных окружения или в коде.")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def send_welcome(message: Message):
    await message.reply("Привет! Я твой бот-напоминалка. Готов к работе!")

@dp.message_handler()
async def echo(message: Message):
    await message.reply(f"Ты сказал: {message.text}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
