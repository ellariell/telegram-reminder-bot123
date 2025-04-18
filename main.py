
import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задано. Убедитесь, что он указан в переменных окружения.")

bot = Bot(
    token=BOT_TOKEN,
    default=Bot.DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=MemoryStorage())
dp.message.middleware(ChatActionMiddleware())

@dp.message(CommandStart())
async def on_start(message: Message):
    await message.answer("<b>Привет!</b> Я успешно работаю на Render 🎉")

@dp.message(F.text)
async def echo(message: Message):
    await message.answer(message.text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
