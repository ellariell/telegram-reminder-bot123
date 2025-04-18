
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiohttp import web

from config import TOKEN, WEBHOOK_PATH, WEBHOOK_URL, WEB_SERVER_HOST, WEB_SERVER_PORT
from handlers.reminders import router as reminder_router
from handlers.commands import router as command_router
from middlewares.check_user import CheckUserMiddleware
from services.scheduler import send_reminder

# Включаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализируем хранилище, бота и диспетчер
storage = MemoryStorage()
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=storage)
dp.include_router(command_router)
dp.include_router(reminder_router)
dp.message.middleware(CheckUserMiddleware())

# Планировщик
scheduler = AsyncIOScheduler()
scheduler.add_job(send_reminder, "interval", seconds=60, id="send_reminder")
scheduler.start()

async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    await bot.session.close()

async def main():
    app = web.Application()
    app["bot"] = bot

    # Регистрируем webhook-хендлер
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)

    # Устанавливаем Webhook
    await on_startup(app)

    # Подключаем shutdown callback
    app.on_shutdown.append(on_shutdown)

    # Запускаем aiohttp сервер
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Бот остановлен!")
