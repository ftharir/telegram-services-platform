from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_language_keyboard() -> InlineKeyboardMarkup:
    """ساخت و دریافت کیبورد اینلاین برای انتخاب یا تغییر زبان کاربر."""
    buttons = [
        [
            InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="lang_fa"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)