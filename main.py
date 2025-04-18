
import os
import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set. Убедитесь, что токен задан в переменных окружения или в коде.")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()

@router.message(commands=["start"])
async def send_welcome(message: Message):
    await message.answer("Привет! Я твой бот-напоминалка. Готов к работе!")

@router.message()
async def echo(message: Message):
    await message.answer(f"Ты сказал: {message.text}")

dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
