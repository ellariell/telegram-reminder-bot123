
import asyncio
import json
import logging
from datetime import datetime, time
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

TOKEN = "7648494160:AAFxkHe-E9-1revY1tMGM1gVFz92L6zaXKI"
USER_ID = 1130771677  # замени на свой Telegram ID

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)
scheduler = AsyncIOScheduler()

history_file = Path("history.json")

def load_history():
    if history_file.exists():
        with open(history_file, "r") as f:
            return json.load(f)
    return {}

def save_history(data):
    with open(history_file, "w") as f:
        json.dump(data, f, indent=2)

completed = load_history()

reminders = [
    ("Подъём", time(5, 50)),
    ("Завтрак", time(6, 10)),
    ("BCAA + Цитруллин", time(15, 45)),
    ("Тренировка", time(16, 10)),
    ("Обед", time(11, 30)),
    ("Ужин", time(18, 0)),
    ("Сон", time(23, 0)),
    ("Таблетки", time(7, 30)),
    ("Вода", time(9, 0)),
]

jokes = {
    "Подъём": ["👀 Подъём, герой! Мир ждёт твоих побед!", "🌅 Новый день — новый шанс! Вставай!"],
    "Завтрак": ["🍳 Завтрак — топливо чемпиона. Не пропускай!", "🥚 Омлет не съест себя сам!"],
    "BCAA + Цитруллин": ["🧪 Пора зарядиться! Размешай шейкер и будь готов к бою!"],
    "Тренировка": ["🏋️‍♂️ Штанга ждёт! А ты готов?", "🔥 Пора качать, а не качаться!"],
    "Обед": ["🍝 Обед — лучший момент восстановиться!", "🥩 Белок зовёт!"],
    "Ужин": ["🍽️ Закрой день по-мужски. Ужин в дело!", "🍲 Без ужина — нет роста."],
    "Сон": ["😴 Хватит листать, пора спать!", "🛌 Регенерация начинается!"],
    "Таблетки": ["💊 Таблетосы в бой!", "🧠 Не забудь, что ты на курсе."],
    "Вода": ["💧 Глотни жизни! Вода решает.", "🚰 Попей, не засохни :)"]
}

def done_button(event_id: str):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Выполнено", callback_data=f"done:{event_id}"))
    return builder.as_markup()

@router.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("👋 Привет! Я твой бот-напоминалка. Я в деле! 🟢")

@router.message(F.text == "/проверка")
async def check_handler(message: Message):
    await message.answer("✅ Бот работает. Напоминания активны.")

async def start_handler(message: Message):
    await message.answer("Привет! Я жив и слежу за твоим режимом 🟢")

async def send_reminder(user_id: int, title: str):
    today = str(datetime.now().date())
    event_id = f"{title}:{today}"
    if completed.get(str(user_id), {}).get(event_id):
        return
    text = f"<b>{title}</b> — {random_message(title)}"
    await bot.send_message(user_id, text, reply_markup=done_button(event_id))

@router.callback_query(F.data.startswith("done:"))
async def handle_done(call: CallbackQuery):
    user_id = str(call.from_user.id)
    event_id = call.data.split(":", 1)[1]
    completed.setdefault(user_id, {})[event_id] = True
    save_history(completed)
    await call.message.edit_text(f"✅ <b>{event_id.split(':')[0]}</b> — выполнено!")

def random_message(title):
    import random
    return random.choice(jokes.get(title, [f"{title} — пора!"]))


@router.message(F.text == "/меню")
async def menu_handler(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Мои напоминания", callback_data="menu:reminders")],
        [InlineKeyboardButton(text="✅ История", callback_data="menu:history")],
        [InlineKeyboardButton(text="🔄 Проверка бота", callback_data="menu:check")]
    ])
    await message.answer("📋 Главное меню:", reply_markup=keyboard)

@router.callback_query(F.data == "menu:reminders")
async def show_reminders(call: CallbackQuery):
    text = "📅 Расписание на сегодня:\n" + "\n".join(f"• {title} — {t.strftime('%H:%M')}" for title, t in reminders)
    await call.message.edit_text(text)

@router.callback_query(F.data == "menu:history")
async def show_history(call: CallbackQuery):
    user_id = str(call.from_user.id)
    today = str(datetime.now().date())
    items = completed.get(user_id, {})
    done_today = [k.split(":")[0] for k in items if k.endswith(today) and items[k]]
    if done_today:
        text = "✅ Выполнено сегодня:\n" + "\n".join(f"• {event}" for event in done_today)
    else:
        text = "❌ Сегодня пока ничего не выполнено."
    await call.message.edit_text(text)

@router.callback_query(F.data == "menu:check")
async def menu_check(call: CallbackQuery):
    await call.message.edit_text("✅ Бот работает. Напоминания активны.")


async def schedule_all():
    for title, t in reminders:
        scheduler.add_job(send_reminder, CronTrigger(hour=t.hour, minute=t.minute), args=(USER_ID, title))

async def main():
    logging.basicConfig(level=logging.INFO)
    await schedule_all()
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
