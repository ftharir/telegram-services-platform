import logging
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.core.config import settings
from app.core.locales import get_text
from app.database.models.user import User
from app.services.user_service import UserService
from app.bot.keyboards import (
    get_main_menu_keyboard,
    get_settings_inline_keyboard,
    get_support_inline_keyboard,
)
from app.bot.keyboards.main_keyboard import get_main_keyboard
from app.bot.middlewares.channel_checker import is_user_member

logger = logging.getLogger(__name__)

router = Router(name="main_router")


@router.message(CommandStart())
async def command_start_handler(message: Message, db_user: User) -> None:
    """هندلر دستور /start - خوش‌آمدگویی و ارائه منوی اصلی."""
    lang = db_user.language_code or "fa"
    welcome_text = get_text("welcome", lang, name=db_user.first_name)
    await message.answer(
        text=welcome_text,
        reply_markup=get_main_menu_keyboard(lang),
    )


@router.callback_query(F.data == "check_channel_join")
async def check_channel_join_callback(callback: CallbackQuery, db_user: User, bot: Bot) -> None:
    """بررسی عضویت هنگام کلیک کاربر روی دکمه «عضو شدم»."""
    lang = db_user.language_code or "fa"
    joined = await is_user_member(bot, callback.from_user.id)

    if joined:
        verified_text = get_text("join_verified", lang)
        if not verified_text or verified_text == "join_verified":
            verified_text = "✅ عضویت شما تایید شد! خوش آمدید."

        await callback.answer(text=verified_text, show_alert=True)
        if callback.message:
            await callback.message.delete()
            await callback.message.answer(
                text=get_text("welcome", lang, name=db_user.first_name),
                reply_markup=get_main_menu_keyboard(lang),
            )
    else:
        not_joined_text = get_text("not_joined_yet", lang)
        if not not_joined_text or not_joined_text == "not_joined_yet":
            not_joined_text = "❌ شما هنوز در کانال عضو نشده‌اید! لطفاً ابتدا عضو شوید."

        await callback.answer(text=not_joined_text, show_alert=True)


@router.message(F.text.in_({"👤 حساب کاربری", "👤 Profile"}))
async def user_profile_handler(message: Message, db_user: User) -> None:
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
    lang = db_user.language_code or "fa"
    await message.answer(
        text=get_text("settings", lang),
        reply_markup=get_settings_inline_keyboard(lang),
    )


@router.message(F.text.in_({"❓ راهنما و پشتیبانی", "❓ Help & Support"}))
async def support_handler(message: Message, db_user: User) -> None:
    lang = db_user.language_code or "fa"
    await message.answer(
        text=get_text("help", lang),
        reply_markup=get_support_inline_keyboard(lang),
    )


@router.message(F.text.in_({"🛠️ سرویس‌ها", "🛠️ Services"}))
async def services_handler(message: Message, db_user: User) -> None:
    lang = db_user.language_code or "fa"
    await message.answer(text=get_text("services", lang), reply_markup=get_main_keyboard())


@router.callback_query(F.data.startswith("lang_"))
async def change_language_callback(
    callback: CallbackQuery,
    user_service: UserService,
    db_user: User,
) -> None:
    new_lang = callback.data.split("_")[1]
    current_lang = db_user.language_code or "fa"
    
    if current_lang == new_lang:
        await callback.answer(text=get_text("lang_already_active", current_lang), show_alert=True)
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
    if callback.message:
        await callback.message.delete()
    await callback.answer()