import asyncio
from datetime import datetime, time
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
import random
import logging
import os

API_TOKEN = os.getenv("API_TOKEN") or "7648494160:AAFxkHe-E9-1revY1tMGM1gVFz92L6zaXKI"

bot = Bot(token=API_TOKEN, default=Bot.create_default(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Расписание задач (время в формате HH:MM)
schedule = {
    "🥣 Завтрак": "06:10",
    "💊 Таблетки": "06:30",
    "💧 Вода": "08:00",
    "🍛 Обед": "11:30",
    "🏋️ Тренировка": "16:30",
    "🍽️ Ужин": "18:00",
    "🌙 Сон": "23:00"
}

# История выполнений
history = {}

# Разнообразные фразы
phrases = [
    "Вперёд, чемпион! 💪",
    "Ну что, пора действовать! 🔥",
    "Твоя цель ждёт тебя 🚀",
    "Не забывай про {} 😎",
    "{} — путь к успеху!"
]

# Кнопка подтверждения
def confirm_kb(task):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Выполнено", callback_data=f"done_{task}")
    return builder.as_markup()

# Отправка напоминаний
async def send_reminders():
    while True:
        now = datetime.now().strftime("%H:%M")
        for task, task_time in schedule.items():
            if now == task_time:
                for chat_id in history:
                    phrase = random.choice(phrases).format(task)
                    await bot.send_message(chat_id, f"<b>{task}</b>
{phrase}", reply_markup=confirm_kb(task))
        await asyncio.sleep(60)

# /start
@dp.message(commands=["start"])
async def start(message: types.Message):
    history[message.chat.id] = []
    await message.answer("Бот активирован! Я буду напоминать тебе о важных вещах 💡")

# Обработка callback
@dp.callback_query()
async def handle_callback(call: types.CallbackQuery):
    if call.data.startswith("done_"):
        task = call.data.split("_", 1)[1]
        history[call.message.chat.id].append((task, datetime.now().strftime("%H:%M")))
        await call.message.edit_text(f"✅ {task} выполнено в {datetime.now().strftime('%H:%M')}")

# Обработка других сообщений
@dp.message()
async def echo(message: types.Message):
    await message.answer("Я бот-напоминалка 🤖. Жду время, чтобы напомнить тебе!")

async def main():
    asyncio.create_task(send_reminders())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())