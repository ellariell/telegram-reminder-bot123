import asyncio
import json
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

reminders = [
    {"time": "05:50", "text": "⏰ Подъём, чемпион!", "type": "wake_up"},
    {"time": "06:10", "text": "🥣 Завтрак. Начни день вкусно!", "type": "breakfast"},
    {"time": "11:30", "text": "🍽 Обед! Подзарядись!", "type": "lunch"},
    {"time": "16:10", "text": "🏋️ Время тренировки. Пора прокачаться!", "type": "workout"},
    {"time": "18:00", "text": "🍲 Ужин. Восстановим силы!", "type": "dinner"},
    {"time": "23:00", "text": "😴 Сон — лучшее восстановление!", "type": "sleep"},
]

async def schedule_reminders(bot: Bot):
    async def send_reminder(reminder):
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Выполнено", callback_data=f"done_{reminder['type']}")
        ]])
        await bot.send_message(chat_id=os.getenv("ADMIN_ID", ""), text=reminder["text"], reply_markup=kb)

    async def scheduler_loop():
        while True:
            now = datetime.now().strftime("%H:%M")
            for rem in reminders:
                if rem["time"] == now:
                    await send_reminder(rem)
            await asyncio.sleep(60)
    asyncio.create_task(scheduler_loop())