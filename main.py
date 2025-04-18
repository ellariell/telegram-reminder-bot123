import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import setup_application
from aiohttp import web

from config import TOKEN, WEBHOOK_PATH, WEBHOOK_URL, WEB_SERVER_HOST, WEB_SERVER_PORT

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

@dp.message()
async def echo(message: types.Message):
    await message.answer("Привет! Это echo бот.")

async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

async def main():
    app = web.Application()
    dp.startup.register(on_startup)
    dp.include_router(dp)
    setup_application(app, dp, path=WEBHOOK_PATH)
    return app

if __name__ == "__main__":
    web.run_app(main(), host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
