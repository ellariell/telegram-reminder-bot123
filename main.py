import asyncio
import logging
import json
from datetime import datetime, time
from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.default import DefaultBotProperties
from aiohttp import web
from utils_notes import parse_note, save_note, get_due_notes

TOKEN = "8096013474:AAHurnRuSxgxfuzYXs3XeGzsFlrExeXdacw"
USER_ID = 1130771677
WEBHOOK_PATH = f"/webhook"
WEBHOOK_SECRET = ""
WEBHOOK_URL = "https://telegram-reminder-bot123.onrender.com"
WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = 8080
LOG_FILE = "reminder_log.json"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Выполнено")],
        [KeyboardButton(text="📋 Меню")]
    ],
    resize_keyboard=True
)

reminders = [
    (time(5, 50), "⏰ Подъём! Доброе утро, чемпион!"),
    (time(6, 30), "💊 Утренние таблетки после еды!"),
    (time(12, 30), "💊 Обеденные таблетки — время подзаправиться!"),
    (time(16, 10), "🏋️‍♂️ Тренировка скоро! Надень кроссовки, настрой плейлист и вперёд!"),
    (time(18, 30), "💊 Вечерние таблетки — завершаем день по правилам!"),
    (time(23, 00), "🌙 Сон! Завтра снова побеждать 💪")
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

@router.message(F.text == "/start")
async def start(message: Message):
    if message.chat.id == USER_ID:
        await message.answer("Привет! Я твой бот-напоминалка 🤖 Готов к труду и отдыху!", reply_markup=kb)

@router.message(F.text == "/check")
async def check(message: Message):
    if message.chat.id == USER_ID:
        await message.answer("✅ Бот работает! Напоминания активны.")

@router.message(F.text == "✅ Выполнено")
async def done(message: Message):
    if message.chat.id == USER_ID:
        log_entry("Пользователь подтвердил выполнение.")
        await message.answer("Отлично! Записал ✅")

@router.message(F.text == "📋 Меню")
async def menu(message: Message):
    if message.chat.id == USER_ID:
        await message.answer("📋 Главное меню открыто", reply_markup=kb)

@router.message()
async def fallback(message: Message):
    if message.chat.id != USER_ID:
        return
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
                await bot.send_message(chat_id=USER_ID, text=text, reply_markup=kb)
                log_entry(f"🔔 Напоминание: {text}")
        due_notes = get_due_notes(USER_ID)
        for note in due_notes:
            await bot.send_message(chat_id=USER_ID, text=f"🔔 Напоминание: {note['text']}")
        await asyncio.sleep(60)

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH, secret_token=WEBHOOK_SECRET)
    asyncio.create_task(scheduler())

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()

async def main():
    app = web.Application()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    logging.info(f"WEBHOOK URL: {WEBHOOK_URL + WEBHOOK_PATH}")
    logging.info(f"Listening on port {WEB_SERVER_PORT}")

    await web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)  # ← исправлено здесь

if __name__ == "__main__":
    asyncio.run(main())

