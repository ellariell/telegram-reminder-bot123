from fastapi import APIRouter, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from config import WEBHOOK_PATH, WEBHOOK_SECRET

router = APIRouter()

def register_webhook(dp: Dispatcher, bot: Bot):
    @router.post(WEBHOOK_PATH)
    async def webhook_handler(request: Request):
        if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
            return Response(status_code=403)
        data = await request.json()
        update = Update.model_validate(data)
        await dp.feed_update(bot, update)
        return Response(status_code=200)