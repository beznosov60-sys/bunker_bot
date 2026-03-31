from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Добро пожаловать в Бункер! Команды: создать игру, присоединиться, начать игру, открыть mini app"
    )


@router.message(F.text.lower() == "открыть mini app")
async def open_mini_app(message: Message) -> None:
    await message.answer("Mini App: https://example.com")
