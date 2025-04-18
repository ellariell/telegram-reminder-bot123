import asyncio
from aiogram import Bot

API_TOKEN = "твой_токен"  # Замени на настоящий токен

bot = Bot(token=API_TOKEN)

async def main():
    user_id = 123456789  # Заменить на реальный user_id
    msg = "Пример сообщения"
    await bot.send_message(chat_id=user_id, text=msg + '\nОтвет: "Выполнено"')

if __name__ == "__main__":
    asyncio.run(main())