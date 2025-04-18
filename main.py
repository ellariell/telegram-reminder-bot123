import logging
from aiogram import Bot, Dispatcher, executor, types
import asyncio
import os
from datetime import datetime

API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

reminder_times = {
    "wake_up": "05:50",
    "breakfast": "06:10",
    "lunch": "11:30",
    "workout1": "16:30",
    "workout2": "17:00",
    "dinner1": "18:00",
    "dinner2": "18:30",
    "sleep": "23:00"
}

messages = {
    "wake_up": ["Доброе утро! Пора вставать и покорять мир 💪"],
    "breakfast": ["Завтрак ждет тебя! Пора зарядиться энергией 🍳"],
    "lunch": ["Обед — это важно! Не забудь поесть 🥗"],
    "workout1": ["Время тренировки! Погнали делать форму 🔥"],
    "workout2": ["Тренировка зовёт! Не проспи прогресс 🏋️"],
    "dinner1": ["Ужин на подходе! Белок сам себя не съест 🍗"],
    "dinner2": ["Если ещё не поел — сейчас самое время! 🥘"],
    "sleep": ["Отбой, герой! Завтра новые свершения 😴"]
}

async def reminder_loop():
    while True:
        now = datetime.now().strftime("%H:%M")
        for key, time in reminder_times.items():
            if now == time:
                for msg in messages.get(key, []):
                    await bot.send_message(chat_id=user_id, text=msg + "\nОтветь: "Выполнено ✅"")
        await asyncio.sleep(60)

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    global user_id
    user_id = message.chat.id
    await message.answer("Привет! Я буду напоминать тебе о важных делах 😊")
    asyncio.create_task(reminder_loop())

@dp.message_handler(lambda message: "выполнено" in message.text.lower())
async def confirm_handler(message: types.Message):
    await message.answer("Отлично! Я записал это 👌")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
