import asyncio
import logging
import json
from datetime import datetime, time
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

BOT_TOKEN = "8096013474:AAHurnRuSxgxfuzYXs3XeGzsFlrExeXdacw"
USER_ID = 1130771677
LOG_FILE = "reminder_log.json"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Клавиатура
kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✅ Выполнено")],
    [KeyboardButton(text="📋 Меню")]
], resize_keyboard=True)

# FSM состояния
class TabletCheck(StatesGroup):
    awaiting_answer = State()

# Напоминания
reminders = [
    (time(5, 50), "⏰ Подъём! Вперёд к победам ☀️"),
    (time(6, 30), "💊 Время утренних таблеток (и я задам вопрос)"),
    (time(11, 30), "🍲 Обед — время подкрепиться!"),
    (time(12, 30), "💊 Таблетки после обеда!"),
    (time(16, 10), "🏋️‍♂️ Тренировка уже рядом — готовься!"),
    (time(18, 0), "🍽️ Ужин! Не забывай поесть!"),
    (time(18, 30), "💊 Вечерние таблетки ждут тебя"),
    (time(23, 0), "🌙 Сон! Пора отдыхать, герой 😴")
]

# Лог
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

# Обработка текстовых команд
@dp.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Я бот-напоминалка и диалоговый помощник 🧠", reply_markup=kb)
    await ask_tablets(message.chat.id, state)

@dp.message(F.text == "/check")
async def check(message: Message):
    await message.answer("✅ Я жив и работаю! Все напоминания активны.")

@dp.message(F.text == "📋 Меню")
async def menu(message: Message):
    await message.answer("📋 Главное меню открыто", reply_markup=kb)

@dp.message(F.text == "✅ Выполнено")
async def done(message: Message):
    log_entry("Пользователь нажал ✅ Выполнено")
    await message.answer("Записал! Красавчик 💪")

@dp.message(TabletCheck.awaiting_answer, F.text.in_(["✅ Да", "❌ Нет"]))
async def handle_answer(message: Message, state: FSMContext):
    if message.text == "✅ Да":
        await message.answer("Отлично! Продолжай в том же духе 😊")
        log_entry("✅ Пользователь подтвердил приём таблеток")
    else:
        await message.answer("Окей, я напомню тебе через 30 минут ⏳")
        log_entry("❌ Пользователь НЕ принял таблетки утром")
        await asyncio.sleep(1800)
        await bot.send_message(chat_id=message.chat.id, text="💊 Эй, не забудь таблетки, пожалуйста!")
    await state.clear()

@dp.message()
async def fallback(message: Message):
    await message.answer("Напиши /start чтобы начать или жди напоминаний ⏰")

async def ask_tablets(chat_id: int, state: FSMContext):
    await bot.send_message(chat_id=chat_id, text="💊 Ты уже принял утренние таблетки?", reply_markup=kb)
    await state.set_state(TabletCheck.awaiting_answer)

# Цикл напоминаний
async def scheduler():
    while True:
        now = datetime.now().time().replace(second=0, microsecond=0)
        for r_time, text in reminders:
            if now == r_time:
                try:
                    if r_time == time(6, 30):
                        ctx = dp.fsm.get_context(bot, USER_ID)
                        await ask_tablets(USER_ID, ctx)
                        log_entry("📤 Автоматический вопрос в 6:30")
                    else:
                        await bot.send_message(chat_id=USER_ID, text=text, reply_markup=kb)
                        log_entry(f"🔔 Напоминание: {text}")
                except Exception as e:
                    logging.error(f"Ошибка напоминания: {e}")
                await asyncio.sleep(60)
        await asyncio.sleep(20)

async def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())