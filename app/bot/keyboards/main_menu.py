from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.core.locales import get_text


def get_main_menu_keyboard(lang: str = "fa") -> ReplyKeyboardMarkup:
    """ساخت کیبورد اصلی متنی متناسب با زبان کاربر (fa/en)."""
    keyboard = [
        [
            KeyboardButton(text=get_text("btn_services", lang)),
            KeyboardButton(text=get_text("btn_profile", lang)),
        ],
        [
            KeyboardButton(text=get_text("btn_settings", lang)),
            KeyboardButton(text=get_text("btn_help", lang)),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        persistent=True,
    )