from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_settings_inline_keyboard() -> InlineKeyboardMarkup:
    """ساخت کیبورد شیشه‌ای (Inline) برای بخش تنظیمات و تغییر زبان."""
    buttons = [
        [
            InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="lang_fa"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ],
        [
            InlineKeyboardButton(text="❌ انصراف", callback_data="close_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_support_inline_keyboard() -> InlineKeyboardMarkup:
    """ساخت کیبورد شیشه‌ای برای بخش پشتیبانی و کانال خبررسانی."""
    buttons = [
        [
            InlineKeyboardButton(text="📢 کانال اطلاع‌رسانی", url="https://t.me/telegram"),
            InlineKeyboardButton(text="💬 ارتباط با پشتیبانی", url="https://t.me/telegram"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)