import asyncio
import logging
import json
from datetime import datetime, time
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from utils_notes import parse_note, save_note, get_due_notes
from aiohttp import web

BOT_TOKEN = "8096013474:AAHurnRuSxgxfuzYXs3XeGzsFlrExeXdacw"
USER_ID = 1130771677
LOG_FILE = "reminder_log.json"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Выполнено")],
        [KeyboardButton(text="📋 Меню")]
    ],
    resize_keyboard=True
)

reminders = [
    (time(5, 50), "⏰ Подъём!"),
    (time(6, 30), "💊 Утренние таблетки!"),
    (time(12, 30), "💊 Таблетки после обеда!"),
    (time(16, 10), "🏋️‍♂️ Тренировка скоро!"),
    (time(18, 30), "💊 Вечерние таблетки!")
]

def log_entry(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = {"time": timestamp, "message": message}
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Привет! Я бот-напоминалка 🤖", reply_markup=kb)

@dp.message(F.text == "/check")
async def check(message: Message):
    await message.answer("✅ Бот работает! Напоминания активны.")

@dp.message(F.text == "✅ Выполнено")
async def done(message: Message):
    log_entry("Пользователь подтвердил выполнение.")
    await message.answer("Отлично! Записал ✅")

@dp.message(F.text == "📋 Меню")
async def menu(message: Message):
    await message.answer("📋 Главное меню открыто", reply_markup=kb)

@dp.message()
async def fallback(message: Message):
    if message.text.lower().startswith("напомни мне"):
        parsed = parse_note(message.text)
        if parsed:
            save_note(message.from_user.id, parsed)
            await message.answer(f"✅ Запомнил: {parsed['text']} в {parsed['time']}")
        else:
            await message.answer("⚠️ Непонятный формат. Пример: напомни мне завтра в 08:00 перевести деньги")
    else:
        await message.answer("Я тебя понял 😉")

async def scheduler():
    while True:
        now = datetime.now().time().replace(second=0, microsecond=0)
        for r_time, text in reminders:
            if now == r_time:
                await bot.send_message(chat_id=USER_ID, text=text)
                log_entry(f"🔔 Напоминание: {text}")
        due_notes = get_due_notes(USER_ID)
        for note in due_notes:
            await bot.send_message(chat_id=USER_ID, text=f"🔔 Напоминание: {note['text']}")
        await asyncio.sleep(60)

async def on_startup(app):
    asyncio.create_task(scheduler())

async def handle(request):
    return web.Response(text="Бот работает 🟢")

app = web.Application()
app.router.add_get("/", handle)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dp.startup.register(on_startup)
    web.run_app(app, port=8080)