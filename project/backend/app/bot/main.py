import asyncio

from aiogram import Bot, Dispatcher

from app.bot.handlers.game import router
from app.config import get_settings


async def run_bot() -> None:
    settings = get_settings()
    if settings.bot_token == "CHANGE_ME":
        raise RuntimeError("Set BOT_TOKEN in .env")
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
