import asyncio
import logging
from datetime import datetime, timedelta
import json
import re

from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

TOKEN = "8096013474:AAHurnRuSxgxfuzYXs3XeGzsFlrExeXdacw"
USER_ID = 1130771677
NOTES_FILE = "user_notes.json"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# Парсинг напоминания
def parse_note(text: str):
    match = re.search(r"(завтра|сегодня)?\s*в\s*(\d{1,2}[:\.]\d{2})\s*(.+)", text.lower())
    if not match:
        return None
    day_word, time_str, note_text = match.groups()

    now = datetime.now()
    hour, minute = map(int, time_str.replace('.', ':').split(":"))
    target_day = now.date()
    if day_word == "завтра":
        target_day += timedelta(days=1)

    target_datetime = datetime.combine(target_day, datetime.min.time()) + timedelta(hours=hour, minutes=minute)
    return {"time": target_datetime.strftime("%Y-%m-%d %H:%M"), "text": note_text.strip()}

# Сохранение
def save_note(user_id: int, note: dict):
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}

    if str(user_id) not in data:
        data[str(user_id)] = []

    data[str(user_id)].append(note)

    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Получение актуальных заметок
def get_due_notes(user_id: int):
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        return []

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    user_notes = data.get(str(user_id), [])
    due = [note for note in user_notes if note["time"] == now]

    data[str(user_id)] = [note for note in user_notes if note["time"] != now]

    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return due

# Команды
@router.message(F.text == "/start")
async def cmd_start(message: Message):
    if message.chat.id == USER_ID:
        await message.answer("Привет! Напиши мне, что и когда напомнить")
Пример: напомни мне завтра в 08:00 выпить воду")

@router.message()
async def handle_note(message: Message):
    if message.chat.id != USER_ID:
        return
    if message.text.lower().startswith("напомни мне"):
        parsed = parse_note(message.text)
        if parsed:
            save_note(message.from_user.id, parsed)
            await message.answer(f"✅ Запомнил: {parsed['text']} в {parsed['time']}")
        else:
            await message.answer("⚠️ Непонятный формат. Пример: напомни мне завтра в 08:00 выпить воду")
    else:
        await message.answer("Напиши, что и когда напомнить.
Пример: напомни мне сегодня в 20:00 позвонить другу")

# Кнопки выбора
@router.callback_query(F.data == "remind_later")
async def remind_later(callback: CallbackQuery):
    try:
        with open("remind_temp.json", "r", encoding="utf-8") as f:
            note = json.load(f)
    except:
        note = {}

    if note:
        dt = datetime.now() + timedelta(minutes=10)
        new_note = {"time": dt.strftime("%Y-%m-%d %H:%M"), "text": note.get("text", "напоминание")}
        save_note(callback.from_user.id, new_note)
        await callback.message.answer("⏳ Напомню через 10 минут.")
    await callback.answer()

@router.callback_query(F.data == "remind_no")
async def remind_no(callback: CallbackQuery):
    await callback.message.answer("Хорошо, не буду напоминать.")
    await callback.answer()

# Планировщик
async def check_reminders():
    print("✅ Планировщик запущен")
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        due_notes = get_due_notes(USER_ID)
        for note in due_notes:
            with open("remind_temp.json", "w", encoding="utf-8") as f:
                json.dump(note, f, ensure_ascii=False)
            await bot.send_message(
                chat_id=USER_ID,
                text=f"🔔 Напоминание: {note['text']}",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔁 Напомнить позже", callback_data="remind_later"),
                     InlineKeyboardButton(text="❌ Не нужно", callback_data="remind_no")]
                ])
            )
        await asyncio.sleep(60)

# Запуск
async def main():
    asyncio.create_task(check_reminders())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
