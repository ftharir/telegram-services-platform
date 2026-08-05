import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    TelegramObject,
    User as TelegramUser,
)

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_join_channel_keyboard(channel_link: str) -> InlineKeyboardMarkup:
    """ساخت کیبورد شیشه‌ای عضویت در کانال."""
    buttons = [
        [InlineKeyboardButton(text="📢 عضویت در کانال / Join Channel", url=channel_link)],
        [InlineKeyboardButton(text="🔄 عضو شدم / Checked", callback_data="check_channel_join")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def is_user_member(bot: Bot, user_id: int) -> bool:
    """استعلام وضعیت عضویت کاربر در کانال."""
    channel_id = getattr(settings, "REQUIRED_CHANNEL_ID", None) or getattr(settings, "required_channel_id", None)
    if not channel_id:
        return True

    try:
        chat_id_param = int(channel_id) if str(channel_id).replace("-", "").isdigit() else channel_id
        member = await bot.get_chat_member(chat_id=chat_id_param, user_id=user_id)
        return member.status not in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]
    except TelegramBadRequest as e:
        logger.debug("User %s is not in channel %s: %s", user_id, channel_id, e)
        return False
    except Exception as e:
        logger.error("Error checking membership for user %s: %s", user_id, e)
        return True


class ForcedMemberMiddleware(BaseMiddleware):
    """میدل‌ور قفل کامل ربات برای کاربران غیرعضو."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        channel_id = getattr(settings, "REQUIRED_CHANNEL_ID", None) or getattr(settings, "required_channel_id", None)
        channel_link = getattr(settings, "CHANNEL_LINK", None) or getattr(settings, "channel_link", "https://t.me/telegram")

        # ۱. اگر کانال ست نشده بود، چک نکن
        if not channel_id:
            return await handler(event, data)

        # ۲. دکمه "عضو شدم" نباید قفل شود
        if isinstance(event, CallbackQuery) and event.data == "check_channel_join":
            return await handler(event, data)

        bot: Bot = data["bot"]
        event_user: TelegramUser | None = data.get("event_from_user")

        if event_user and not event_user.is_bot:
            joined = await is_user_member(bot, event_user.id)
            if not joined:
                must_join_text = (
                    "⚠️ <b>عضویت در کانال الزامی است!</b>\n\n"
                    "برای استفاده از خدمات ربات، ابتدا در کانال ما عضو شده و سپس روی دکمه <b>«عضو شدم 🔄»</b> کلیک کنید."
                )
                keyboard = get_join_channel_keyboard(channel_link)

                if isinstance(event, Message):
                    await event.answer(text=must_join_text, reply_markup=keyboard)
                elif isinstance(event, CallbackQuery):
                    await event.message.answer(text=must_join_text, reply_markup=keyboard)
                    await event.answer(text="❌ شما هنوز در کانال عضو نشده‌اید!", show_alert=True)

                # متوقف کردن ادامه دسترسی
                return

        return await handler(event, data)