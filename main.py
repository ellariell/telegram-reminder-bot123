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
from utils_notes import parse_note, save_note, get_due_notes

BOT_TOKEN = "8096013474:AAHurnRuSxgxfuzYXs3XeGzsFlrExeXdacw"
USER_ID = 1130771677
LOG_FILE = "reminder_log.json"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Постоянная клавиатура
kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Выполнено")],
        [KeyboardButton(text="📋 Меню")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери действие 👇"
)

# FSM состояние
class TabletCheck(StatesGroup):
    awaiting_answer = State()

# Юморные фразы
jokes = [
    "🧠 Не забудь таблетосы — они тебя тоже не забывают!",
    "💡 Таблетки не выпьешь — мышц не будет!",
    "🥼 Один таблеткин в день — и ты не в группе риска 😄"
]

# Расписание напоминаний
reminders = [
    (time(5, 50), "⏰ Подъём! Вперёд к победам ☀️"),
    (time(6, 30), "💊 Утренние таблетки! " + jokes[0]),
    (time(11, 30), "🍲 Обед! Дай организму белок и любовь"),
    (time(12, 30), "💊 Время таблеток после обеда! " + jokes[1]),
    (time(16, 10), "🏋️‍♂️ Подготовка к тренировке — надень кроссы и настрой плейлист!"),
    (time(18, 0), "🍽️ Ужин! Без него ни мышцы, ни сила 😉"),
    (time(18, 30), "💊 Вечерние таблетки! " + jokes[2]),
    (time(23, 0), "🌙 Отбой, чемпион. Восстановление начинается со сна 😴")
]

# Логирование
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

# Команды
@dp.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await message.answer("Привет, я бот-напоминалка 💊
Я помогу тебе не забыть о важном!", reply_markup=kb)
    await ask_tablets(message.chat.id, state)

@dp.message(F.text == "/check")
async def check(message: Message):
    await message.answer("✅ Бот жив и работает! Все напоминания активны.")

@dp.message(F.text == "📋 Меню")
async def menu(message: Message):
    await message.answer("📋 Главное меню. Жди напоминаний или добавь новое — просто напиши", reply_markup=kb)

@dp.message(F.text == "✅ Выполнено")
async def done(message: Message):
    log_entry("Пользователь нажал ✅ Выполнено")
    await message.answer("Хорош! Записал в журнал 📒")

# Ответ на диалог утром
@dp.message(TabletCheck.awaiting_answer, F.text.in_(["✅ Да", "❌ Нет"]))
async def handle_answer(message: Message, state: FSMContext):
    if message.text == "✅ Да":
        await message.answer("Красава 💪 Продолжай в том же духе!")
        log_entry("✅ Пользователь подтвердил приём таблеток")
    else:
        await message.answer("Напомню через 30 минут! 📣")
        log_entry("❌ Пользователь не принял таблетки утром")
        await asyncio.sleep(1800)
        await bot.send_message(chat_id=message.chat.id, text="💊 Напоминаю: таблетки ещё ждут тебя!")
    await state.clear()

@dp.message()
async def fallback(message: Message, state: FSMContext):
    if message.text.lower().startswith("напомни мне"):
        parsed = parse_note(message.text)
        if parsed:
            save_note(message.from_user.id, parsed)
            await message.answer(f"✅ Запомнил! Напомню тебе: {parsed['text']} в {parsed['time']}")
        else:
            await message.answer("⚠️ Не понял. Пример: напомни мне завтра в 08:00 перевести деньги другу")
        return
    await message.answer("Напиши /start чтобы начать или жди ⏰")

async def ask_tablets(chat_id: int, state: FSMContext):
    await bot.send_message(chat_id=chat_id, text="Ты уже принял утренние таблетки? 💊", reply_markup=kb)
    await state.set_state(TabletCheck.awaiting_answer)

async def scheduler():
    while True:
        now = datetime.now().time().replace(second=0, microsecond=0)
        for r_time, text in reminders:
            if now == r_time:
                try:
                    if r_time == time(6, 30):
                        ctx = dp.fsm.get_context(bot, USER_ID)
                        await ask_tablets(USER_ID, ctx)
                        log_entry("📤 Утренний вопрос в 6:30")
                    else:
                        await bot.send_message(chat_id=USER_ID, text=text, reply_markup=kb)
                        log_entry(f"🔔 Напоминание: {text}")
                except Exception as e:
                    logging.error(f"Ошибка напоминания: {e}")
        due_notes = get_due_notes(USER_ID)
        for note in due_notes:
            await bot.send_message(chat_id=USER_ID, text=f"🔔 Напоминание: {note['text']}")
        await asyncio.sleep(60)

async def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())