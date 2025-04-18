from aiogram.client.default import DefaultBotProperties
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import setup_application, SimpleRequestHandler
from aiohttp import web
from dotenv import load_dotenv

from config import WEBHOOK_PATH, WEBHOOK_SECRET, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_URL
from reminders import schedule_all_reminders
from utils import main_menu_keyboard as main_menu_kb

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

@dp.message(F.text, F.text.lower() == "меню")
async def show_menu(message: Message):
    await message.answer("📋 Главное меню:", reply_markup=main_menu_kb())

async def on_startup(dispatcher: Dispatcher, bot: Bot):
    await schedule_all_reminders(bot)
    logging.info("🔔 Напоминания запущены")

async def main():
    app = web.Application()
    dp.startup.register(on_startup)
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    await bot.set_webhook(WEBHOOK_URL, secret_token=WEBHOOK_SECRET)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())