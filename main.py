
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from utils_notes import router, scheduler

TOKEN = "8096013474:AAHurnRuSxgxfuzYXs3XeGzsFlrExeXdacw"  # ← твой токен

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
dp.include_router(router)

async def main():
    # Запускаем планировщик в фоне
    asyncio.create_task(scheduler())
    logging.info("Бот и планировщик запущены")

    # Стартуем polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
