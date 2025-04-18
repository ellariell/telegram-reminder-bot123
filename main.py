import asyncio
import logging
from datetime import time, datetime
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart

TOKEN = "7968749408:AAFOgRg8mKlVAzTWlgjdMOcj33hnYe2vM-Q"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(CommandStart())
async def on_start(message: Message):
    await message.answer("Привет! Я бот-напоминалка 😊 Готов к работе!")

@dp.message(F.text.lower().in_({"как дела", "как ты", "что ты там"}))
async def mood_handler(message: Message):
    await message.answer("Я в порядке, главное — не забывай про тренировку 😎")

@dp.message(F.text)
async def echo_handler(message: Message):
    await message.answer(f"Ты сказал: {message.text}")

async def send_reminder(chat_id: int, task: str):
    await bot.send_message(chat_id, f"<b>{task}</b>")

async def reminder_loop(chat_id: int):
    while True:
        now = datetime.now().time()

        schedule = {
            time(5, 50): "Подъём, боец! 👀",
            time(6, 10): "Завтрак — важен, как штанга! 🍳",
            time(11, 30): "Обеденный сигнал! 🔔",
            time(16, 30): "Время кача! 🏋️‍♂️",
            time(18, 0): "Ужинать пора! 🍽",
            time(23, 0): "Отбой! Спокойной ночи 🛌"
        }

        for task_time, task_text in schedule.items():
            if now.hour == task_time.hour and now.minute == task_time.minute:
                await send_reminder(chat_id, task_text)
                await asyncio.sleep(60)

        await asyncio.sleep(20)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())