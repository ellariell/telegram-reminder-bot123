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
LOG_FILE = "tablet_dialog_log.json"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# FSM состояния
class TabletCheck(StatesGroup):
    awaiting_answer = State()

# Кнопки
kb_yes_no = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")]
], resize_keyboard=True)

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

@dp.message(commands=["start"])
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Я бот, который заботится о твоих таблетках 💊", reply_markup=kb_yes_no)
    await ask_tablets(message.chat.id, state)

@dp.message(TabletCheck.awaiting_answer, F.text.in_(["✅ Да", "❌ Нет"]))
async def handle_answer(message: Message, state: FSMContext):
    if message.text == "✅ Да":
        await message.answer("Отлично! Рад это слышать 😊")
        log_entry("✅ Пользователь подтвердил приём таблеток")
    else:
        await message.answer("Окей, напомню тебе через 30 минут ⏳")
        log_entry("❌ Пользователь НЕ принял таблетки")
        await asyncio.sleep(1800)
        await bot.send_message(chat_id=message.chat.id, text="💊 Напоминаю: пора всё-таки принять таблетки!")
    await state.clear()

@dp.message()
async def fallback(message: Message):
    await message.answer("Напиши /start чтобы начать диалог 💬")

# Отправка вопроса
async def ask_tablets(chat_id: int, state: FSMContext):
    await bot.send_message(chat_id=chat_id, text="💊 Ты уже принял утренние таблетки?", reply_markup=kb_yes_no)
    await state.set_state(TabletCheck.awaiting_answer)

# Фоновая задача — запускает диалог в 6:30 каждый день
async def scheduler():
    while True:
        now = datetime.now().time().replace(second=0, microsecond=0)
        if now == time(6, 30):
            try:
                ctx = dp.fsm.get_context(bot, USER_ID)
                await ask_tablets(USER_ID, ctx)
                log_entry("📤 Автоматически задан вопрос о таблетках в 6:30")
            except Exception as e:
                logging.error(f"Ошибка автозапуска: {e}")
            await asyncio.sleep(60)
        await asyncio.sleep(30)

async def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())