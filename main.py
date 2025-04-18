import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, time
import logging

BOT_TOKEN = "8096013474:AAHurnRuSxgxfuzYXs3XeGzsFlrExeXdacw"
USER_ID = 1130771677

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

reminders = [
    (time(5, 50), "⏰ Вставай, чемпион! Новый день уже тут 💪"),
    (time(6, 30), "💊 Не забудь утренние таблетки (после еды)!"),
    (time(12, 30), "💊 Время обеденных таблеток — не пропусти!"),
    (time(18, 30), "💊 Вечер настал — таблетки ждут тебя!"),
]

kb_done = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✅ Выполнено")]
], resize_keyboard=True)

@dp.message(F.text.lower() == "меню")
async def menu(message: Message):
    await message.answer("📋 Меню. Всё под контролем 👍", reply_markup=kb_done)

@dp.message(F.text == "✅ Выполнено")
async def confirm(message: Message):
    await message.answer("Отмечено! Красавчик 🧠")

@dp.message(commands=["start"])
async def start(message: Message):
    await message.answer("Привет! Я твой бот-напоминалка 🔔 Жди напоминаний и пиши «меню» когда захочешь.")

async def reminder_loop():
    while True:
        now = datetime.now().time().replace(second=0, microsecond=0)
        for r_time, r_text in reminders:
            if now == r_time:
                try:
                    await bot.send_message(chat_id=USER_ID, text=r_text, reply_markup=kb_done)
                except Exception as e:
                    logging.error(f"Ошибка отправки напоминания: {e}")
        await asyncio.sleep(60)

async def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(reminder_loop())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())