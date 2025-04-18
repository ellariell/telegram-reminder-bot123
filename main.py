
import asyncio
import json
import logging
import os
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

load_dotenv()

TOKEN = "7648494160:AAFxkHe-E9-1revY1tMGM1gVFz92L6zaXKI"
USER_ID = 1130771677
HISTORY_FILE = "history.json"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
scheduler = AsyncIOScheduler()
completed = {}

humor_variants = {'Подъём': ['⏰ Подъём, герой! Мир ждёт твоих побед!', 'Просыпайся! Даже будильник уже ушёл на работу 😄', 'Пора вставать! Успех не любит тех, кто дремлет 😉'], 'Таблетки': ['💊 Таблетки ждут! Не обижай их 😂', 'Тело скажет спасибо, если ты не забудешь про таблетки!', 'Лечиться — модно. 💊 Пора принять!'], 'Тренировка': ['🏋️\u200d♂️ Пора качать банку! Будущее тело не построит себя само!', 'Штанга уже скучает. Тренировка ждёт 💪', 'Хватит сидеть! Пора прокачаться!'], 'Сон': ['🌙 Сон — лучший восстановитель. Отбой, чемпион!', 'Засыпай красиво, просыпайся сильным 😴', 'Пора спать. Даже протеин уже лёг в кровать!']}

if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        completed = json.load(f)

reminders = [
    ("⏰ Подъём", "05:50"),
    ("🥣 Завтрак", "06:10"),
    ("💊 Таблетки (утро)", "07:30"),
    ("🚰 Вода", "09:00"),
    ("🍽 Обед", "11:30"),
    ("💊 Таблетки (обед)", "13:30"),
    ("⚡️ Цитруллин + BCAA", "15:45"),
    ("🏋️ Тренировка", "16:10"),
    ("🍲 Ужин", "18:00"),
    ("💊 Таблетки (вечер)", "20:30"),
    ("🌙 Сон", "23:00")
]
    ("⏰ Подъём", "05:50"),
    ("🥣 Завтрак", "06:10"),
    ("💊 Таблетки", "07:30"),
    ("🚰 Вода", "09:00"),
    ("🍽 Обед", "11:30"),
    ("⚡️ Цитруллин + BCAA", "15:45"),
    ("🏋️ Тренировка", "16:10"),
    ("🍲 Ужин", "18:00"),
    ("🌙 Сон", "23:00")
]

def get_keyboard(key: str):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Выполнено", callback_data=f"done:{key}")
    ]])

def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(completed, f, indent=2)


async def send_reminder(title: str, key: str):
    today = str(datetime.now().date())
    user_data = completed.setdefault(str(USER_ID), {})
    if user_data.get(f"{key}:{today}"):
        return

    humor = None
    for k in humor_variants:
        if k.lower() in title.lower():
            humor = random.choice(humor_variants[k])
            break
    if not humor:
        humor = f"{title} — пора! ⏳"

    kb = get_keyboard(key)
    await bot.send_message(chat_id=USER_ID, text=humor, reply_markup=kb)

    today = str(datetime.now().date())
    user_data = completed.setdefault(str(USER_ID), {})
    if user_data.get(f"{key}:{today}"):
        return
    await bot.send_message(chat_id=USER_ID, text=f"{title} — пора! ⏳", reply_markup=get_keyboard(key))

@dp.callback_query(F.data.startswith("done:"))
async def on_done(callback: CallbackQuery):
    key = callback.data.split(":")[1]
    today = str(datetime.now().date())
    completed.setdefault(str(USER_ID), {})[f"{key}:{today}"] = True
    save_history()
    await callback.message.edit_text(f"✅ {key} выполнено!")

@dp.message(F.text == "/start")
async def start(message: Message):
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(types.KeyboardButton(text="/меню"))
    await message.answer("👋 Привет! Я жив и работаю 🟢")

@dp.message(F.text == "/проверка")
async def check(message: Message):
    await message.answer("✅ Бот работает. Напоминания активны.")

@dp.message(F.text == "/меню")
async def menu(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Расписание", callback_data="menu:schedule")],
        [InlineKeyboardButton(text="✅ История", callback_data="menu:history")],
        [InlineKeyboardButton(text="🔄 Проверка", callback_data="menu:check")]
    ])
    await message.answer("📋 Главное меню:", reply_markup=kb)

@dp.callback_query(F.data == "menu:schedule")
async def show_schedule(call: CallbackQuery):
    text = "\n".join([f"• {title} — {time}" for title, time in reminders])
    await call.message.edit_text(f"📅 Расписание на день:\n{text}")

@dp.callback_query(F.data == "menu:history")
async def show_history(call: CallbackQuery):
    user_id = str(call.from_user.id)
    today = str(datetime.now().date())
    items = completed.get(user_id, {})
    done_today = [k.split(":")[0] for k in items if k.endswith(today) and items[k]]
    if done_today:
        text = "✅ Выполнено сегодня:\n" + "\n".join([f"• {e}" for e in done_today])
    else:
        text = "Сегодня ещё ничего не выполнено ❌"
    await call.message.edit_text(text)

@dp.callback_query(F.data == "menu:check")
async def show_check(call: CallbackQuery):
    await call.message.edit_text("✅ Бот работает. Напоминания активны.")

def schedule_all():
    for title, time_str in reminders:
        hour, minute = map(int, time_str.split(":"))
        key = title.strip("⏰🥣💊🚰🍽⚡️🏋️🍲🌙 ").strip()
        scheduler.add_job(send_reminder, trigger="cron", hour=hour, minute=minute, args=[title, key])

async def main():
    scheduler.start()
    schedule_all()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
