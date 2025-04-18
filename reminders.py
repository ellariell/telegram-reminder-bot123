import asyncio
import json
import random
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from messages import wake_messages, meal_messages, pill_messages, workout_messages, sleep_messages

history_file = "history.json"

def log_event(event):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
    except:
        history = []
    history.append({"timestamp": now, "event": event})
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def confirmation_keyboard(task):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Выполнено", callback_data=f"done:{task}")
    ]])

async def send_reminder(bot, user_id, message_list, task_name):
    message = random.choice(message_list)
    await bot.send_message(chat_id=user_id, text=message, reply_markup=confirmation_keyboard(task_name))

async def reminder_loop(bot, user_id, schedule):
    while True:
        now = datetime.now().time()
        for item in schedule:
            if now.hour == item["hour"] and now.minute == item["minute"]:
                await send_reminder(bot, user_id, item["messages"], item["task"])
                log_event(item["task"])
                await asyncio.sleep(60)
        await asyncio.sleep(10)

async def schedule_all_reminders(bot):
    from dotenv import load_dotenv
    import os
    load_dotenv()
    user_id = int(os.getenv("USER_ID"))

    schedule = [
        {"hour": 5, "minute": 50, "messages": wake_messages, "task": "wake_up"},
        {"hour": 6, "minute": 10, "messages": meal_messages, "task": "breakfast"},
        {"hour": 6, "minute": 30, "messages": pill_messages, "task": "morning_pills"},
        {"hour": 11, "minute": 30, "messages": meal_messages, "task": "lunch"},
        {"hour": 11, "minute": 50, "messages": pill_messages, "task": "afternoon_pills"},
        {"hour": 16, "minute": 10, "messages": workout_messages, "task": "workout"},
        {"hour": 18, "minute": 0, "messages": meal_messages, "task": "dinner"},
        {"hour": 18, "minute": 20, "messages": pill_messages, "task": "evening_pills"},
        {"hour": 23, "minute": 0, "messages": sleep_messages, "task": "sleep"},
    ]

    asyncio.create_task(reminder_loop(bot, user_id, schedule))