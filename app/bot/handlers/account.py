import logging
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.wallet_service import WalletService

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text.in_({"💰 حساب کاربری", "/account", "Account"}))
async def handle_account_info(message: Message, session: AsyncSession):
    """نمایش موجودی سکه و ۵ تراکنش اخیر کاربر"""
    user_id = message.from_user.id
    wallet_service = WalletService(session)
    
    balance = await wallet_service.get_balance(user_id)
    transactions = await wallet_service.get_user_transactions(user_id, limit=5)
    
    text = f"👤 **حساب کاربری شما**\n\n"
    text += f"💰 **موجودی سکه:** `{balance}` سکه\n\n"
    text += "📜 **تراکنش‌های اخیر:**\n"
    
    if not transactions:
        text += "_هیچ تراکنشی ثبت نشده است._"
    else:
        for tx in transactions:
            sign = "+" if tx.amount > 0 else ""
            text += f"• {tx.description or tx.transaction_type.value}: `{sign}{tx.amount}` سکه\n"
            
    await message.answer(text, parse_mode="Markdown")
