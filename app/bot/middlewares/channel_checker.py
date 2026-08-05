import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, TelegramObject, User as TelegramUser

from app.core.config import settings
from app.core.locales import get_text
from app.database.models.user import User

logger = logging.getLogger(__name__)


def get_join_channel_keyboard(channel_link: str, lang: str = "fa") -> InlineKeyboardMarkup:
    """ساخت کیبورد شیشه‌ای عضویت در کانال و بررسی مجدد."""
    buttons = [
        [
            InlineKeyboardButton(text=get_text("btn_join_channel", lang), url=channel_link),
        ],
        [
            InlineKeyboardButton(text=get_text("btn_check_join", lang), callback_data="check_channel_join"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


class ForcedMemberMiddleware(BaseMiddleware):
    """میدل‌ور بررسی عضویت اجباری کاربر در کانال پشتیبانی/اطلاع‌رسانی."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # اگر شناسه کانال در تنظیمات مشخص نشده باشد، میدل‌ور رد می‌شود
        channel_id = getattr(settings, "required_channel_id", None)
        channel_link = getattr(settings, "required_channel_link", "https://t.me/telegram")
        
        if not channel_id:
            return await handler(event, data)

        bot: Bot = data["bot"]
        event_user: TelegramUser | None = data.get("event_from_user")
        db_user: User | None = data.get("db_user")
        lang = db_user.language_code if db_user else "fa"

        # استثناها: کلیک روی دکمه تایید عضویت نباید بلاک شود
        callback_query = data.get("callback_query")
        if callback_query and callback_query.data == "check_channel_join":
            return await handler(event, data)

        if event_user and not event_user.is_bot:
            try:
                member = await bot.get_chat_member(chat_id=channel_id, user_id=event_user.id)
                # اگر وضعیت کاربر جزو حالات لغو یا خارج‌شده باشد
                if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
                    prompt_text = get_text("must_join_channel", lang)
                    
                    if hasattr(event, "message") and event.message:
                        await event.message.answer(
                            text=prompt_text,
                            reply_markup=get_join_channel_keyboard(channel_link, lang),
                        )
                    elif hasattr(event, "callback_query") and event.callback_query:
                        await event.callback_query.message.answer(
                            text=prompt_text,
                            reply_markup=get_join_channel_keyboard(channel_link, lang),
                        )
                    return  # متوقف کردن ادامه زنجیره اجرا
            except Exception as e:
                logger.warning("Error checking channel membership for user %s: %s", event_user.id, e)

        return await handler(event, data)