import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from datetime import datetime

TOKEN = "7648494160:AAFxkHe-E9-1revY1tMGM1gVFz92L6zaXKI"

dp = Dispatcher()
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)

tasks_done = set()

reminders = {
    "05:50": "🌞 Подъём, чемпион! День ждёт тебя!",
    "06:10": "🍳 Завтрак — топливо для побед!",
    "11:30": "🍱 Обеденный рывок — время зарядиться!",
    "16:30": "🏋️‍♂️ Вперёд на тренировку! Или 17:00, если опаздываешь ;)",
    "18:00": "🍽️ Ужин настал! Или в 18:30 — выбирай!",
    "23:00": "🌙 Сон — суперсила восстановления. Отбой!",
}

confirm_phrases = ["выполнено", "сделано", "готово", "ок", "да", "✔️"]

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! Я бот-напоминалка с юмором 😎 Погнали!")

@dp.message()
async def handle_message(message: Message):
    user_text = message.text.strip().lower()

    if any(p in user_text for p in confirm_phrases):
        tasks_done.add(datetime.now().strftime("%H:%M"))
        await message.answer('Ответ: "Выполнено"')
    else:
        await message.answer('Ответ: "Выполнено"')  # Можно изменить, если нужно другое поведение

async def scheduler():
    while True:
        now = datetime.now().strftime("%H:%M")
        if now in reminders and now not in tasks_done:
            for chat_id in [YOUR_CHAT_ID_HERE]:  # замени на нужный chat_id
                task = reminders[now]
                await bot.send_message(chat_id, f"<b>{task}</b>")
        await asyncio.sleep(60)

async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
