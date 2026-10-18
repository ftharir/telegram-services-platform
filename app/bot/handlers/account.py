from aiogram import Router, F
from aiogram.types import Message
from app.database.session import async_session_maker
from app.services.wallet_service import WalletService
from app.database.repositories.user_repository import UserRepository

router = Router()

@router.message(F.text.contains("حساب کاربری"))
async def show_account_info(message: Message):
    async with async_session_maker() as session:
        wallet_service = WalletService(session)
        user_repo = UserRepository(session)
        
        db_user = await user_repo.get_by_telegram_id(message.from_user.id)
        target_user_id = db_user.id if db_user else message.from_user.id
        
        balance = await wallet_service.get_balance(target_user_id)
        
        text = (
            f"👤 **پروفایل کاربری شما**\n\n"
            f"🆔 **شناسه تلگرام:** `{message.from_user.id}`\n"
            f"👤 **نام:** {message.from_user.full_name or ''}\n"
            f"💰 **موجودی کیف‌پول:** **{balance}** سکه"
        )
        await message.answer(text, parse_mode="Markdown")
