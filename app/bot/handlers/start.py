from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.database.models.user import User

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, db_user: User | None = None) -> None:
    user_name = db_user.first_name if db_user else message.from_user.first_name
    await message.answer(f"سلام {user_name} عزیز! به ربات خدمات تلگرام خوش آمدید. 🌹")