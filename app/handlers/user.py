from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Hi! I'm EchoBot. Send me any message and I'll reply!")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📚 <b>Commands:</b>\n"
        "/start - Start bot\n"
        "/help - Help\n"
        "/echo - Enable echo mode"
    )


@router.message()
async def echo(message: Message):
    await message.answer(message.text)