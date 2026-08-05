import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatMemberStatus

from app.core.config import settings
from app.core.locales import get_text
from app.database.models.user import User
from app.services.user_service import UserService
from app.bot.keyboards import (
    get_main_menu_keyboard,
    get_settings_inline_keyboard,
    get_support_inline_keyboard,
)

logger = logging.getLogger(__name__)

router = Router(name="main_router")


@router.message(CommandStart())
async def command_start_handler(message: Message, db_user: User) -> None:
    """هندلر دستور /start - خوش‌آمدگویی و ارائه کیبورد منوی اصلی به زبان کاربر."""
    lang = db_user.language_code or "fa"
    welcome_text = get_text("welcome", lang, name=db_user.first_name)
    
    await message.answer(
        text=welcome_text,
        reply_markup=get_main_menu_keyboard(lang),
    )


@router.message(F.text.in_({"👤 حساب کاربری", "👤 Profile"}))
async def user_profile_handler(message: Message, db_user: User) -> None:
    """نمایش مشخصات کاربر بر اساس داده‌های PostgreSQL و زبان فعال."""
    lang = db_user.language_code or "fa"
    created_at_str = db_user.created_at.strftime("%Y-%m-%d %H:%M") if db_user.created_at else "N/A"
    
    profile_text = get_text(
        "profile",
        lang,
        telegram_id=db_user.telegram_id,
        first_name=db_user.first_name,
        username=db_user.username or ("ثبت نشده" if lang == "fa" else "Not set"),
        language="فارسی 🇮🇷" if lang == "fa" else "English 🇬🇧",
        created_at=created_at_str,
    )
    await message.answer(text=profile_text)


@router.message(F.text.in_({"⚙️ تنظیمات", "⚙️ Settings"}))
async def settings_handler(message: Message, db_user: User) -> None:
    """نمایش منوی تنظیمات با دکمه‌های Inline تغییر زبان."""
    lang = db_user.language_code or "fa"
    settings_text = get_text("settings", lang)
    
    await message.answer(
        text=settings_text,
        reply_markup=get_settings_inline_keyboard(lang),
    )


@router.message(F.text.in_({"❓ راهنما و پشتیبانی", "❓ Help & Support"}))
async def support_handler(message: Message, db_user: User) -> None:
    """نمایش راهنما و دکمه‌های پشتیبانی متناسب با زبان کاربر."""
    lang = db_user.language_code or "fa"
    help_text = get_text("help", lang)
    
    await message.answer(
        text=help_text,
        reply_markup=get_support_inline_keyboard(lang),
    )


@router.message(F.text.in_({"🛠️ سرویس‌ها", "🛠️ Services"}))
async def services_handler(message: Message, db_user: User) -> None:
    """نمایش لیست سرویس‌های فعال (سرویس‌های آینده در فازهای بعدی متصل می‌شوند)."""
    lang = db_user.language_code or "fa"
    services_text = get_text("services", lang)
    
    await message.answer(text=services_text)


# --- Callback Query Handlers ---

@router.callback_query(F.data.startswith("lang_"))
async def change_language_callback(
    callback: CallbackQuery,
    user_service: UserService,
    db_user: User,
) -> None:
    """تغییر زبان کاربر در PostgreSQL و آپدیت کیبوردهای تلگرام."""
    new_lang = callback.data.split("_")[1]
    current_lang = db_user.language_code or "fa"
    
    if current_lang == new_lang:
        alert_msg = get_text("lang_already_active", current_lang)
        await callback.answer(text=alert_msg, show_alert=True)
        return

    await user_service.change_user_language(db_user.telegram_id, new_lang)
    await callback.answer(text="زبان تغییر یافت / Language updated", show_alert=False)

    if callback.message:
        await callback.message.edit_text(
            text=get_text("lang_changed", new_lang),
            reply_markup=get_settings_inline_keyboard(new_lang),
        )
        await callback.message.answer(
            text=get_text("welcome", new_lang, name=db_user.first_name),
            reply_markup=get_main_menu_keyboard(new_lang),
        )


@router.callback_query(F.data == "close_menu")
async def close_menu_callback(callback: CallbackQuery) -> None:
    """حذف پیام حاوی منوی Inline."""
    if callback.message:
        await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data == "check_channel_join")
async def check_channel_join_callback(
    callback: CallbackQuery,
    db_user: User,
) -> None:
    """بررسی مجدد عضویت کاربر هنگام کلیک روی دکمه تایید عضویت."""
    lang = db_user.language_code or "fa"
    channel_id = getattr(settings, "required_channel_id", None)

    if not channel_id:
        await callback.answer(text=get_text("join_verified", lang), show_alert=True)
        if callback.message:
            await callback.message.delete()
        return

    try:
        member = await callback.bot.get_chat_member(chat_id=channel_id, user_id=callback.from_user.id)
        if member.status not in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
            await callback.answer(text=get_text("join_verified", lang), show_alert=True)
            if callback.message:
                await callback.message.delete()
                await callback.message.answer(
                    text=get_text("welcome", lang, name=db_user.first_name),
                    reply_markup=get_main_menu_keyboard(lang),
                )
        else:
            await callback.answer(text=get_text("not_joined_yet", lang), show_alert=True)
    except Exception as e:
        logger.error("Error verifying channel join: %s", e)
        await callback.answer(text="خطا در اعتبارسنجی / Validation Error", show_alert=True)