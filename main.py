import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

API_TOKEN = "7648494160:AAFxkHe-E9-1revY1tMGM1gVFz92L6zaXKI"

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.chat.id
    msg = message.text
    await bot.send_message(chat_id=user_id, text=msg + '\nОтвет: "Выполнено"')


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())