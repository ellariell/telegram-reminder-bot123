
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message()
async def handler(message: types.Message) -> None:
    msg = message.text
    user_id = message.chat.id

    if msg == "ping":
        await bot.send_message(chat_id=user_id, text="pong")
    elif msg == "/start":
        await bot.send_message(chat_id=user_id, text="Бот запущен.")

    await bot.send_message(chat_id=user_id, text=msg + "\nОтвет: "Выполнено"")

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
