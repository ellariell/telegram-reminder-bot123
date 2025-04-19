import asyncio
import logging
import json
from datetime import datetime, time
from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from utils_notes import parse_note, save_note, get_due_notes

TOKEN = "8096013474:AAHurnRuSxgxfuzYXs3XeGzsFlrExeXdacw"
USER_ID = 1130771677
LOG_FILE = "reminder_log.json"

logging.basicConfig(level=logging.INFO)

from aiogram.client.default import DefaultBotProperties
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
    (time(23, 0), "🌙 Сон! Завтра снова побеждать 💪")
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


async def check_reminders():
    print("✅ check_reminders запущена")
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Проверим регулярные напоминания
        current_time = datetime.now().time().replace(second=0, microsecond=0)
        for r_time, text in reminders:
            if current_time == r_time:
                print(f"🔔 Отправка регулярного напоминания: {text}")
                await bot.send_message(chat_id=USER_ID, text=text, reply_markup=kb)
                log_entry(f"🔔 Напоминание: {text}")

        # Проверим пользовательские напоминания
        due_notes = get_due_notes(USER_ID)
        for note in due_notes:
            print(f"🔔 Отправка пользовательского напоминания: {note['text']}")
            await bot.send_message(
                chat_id=USER_ID,
                text=f"🔔 Напоминание: {note['text']}",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔁 Напомнить позже", callback_data="remind_later"),
                     InlineKeyboardButton(text="❌ Не нужно", callback_data="remind_no")]
                ])
            )
        await asyncio.sleep(60)


async def main():
    asyncio.create_task(check_reminders())
    logging.info("✅ Бот запущен. Ожидаем команды.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

@dp.callback_query(F.data == "remind_later")
async def remind_later_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("last_reminder", "Без текста")
    reminder_time = datetime.now() + timedelta(minutes=10)
    REMINDERS.append({
        "chat_id": callback.message.chat.id,
        "text": text,
        "time": reminder_time.strftime("%Y-%m-%d %H:%M")
    })
    await callback.message.answer(f"⏳ Хорошо, напомню через 10 минут.")
    await callback.answer()


@dp.callback_query(F.data == "remind_no")
async def remind_no_callback(callback: CallbackQuery):
    await callback.message.answer("✅ Хорошо, не буду напоминать.")
    await callback.answer()
