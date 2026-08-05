from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_settings_inline_keyboard(current_lang: str = "fa") -> InlineKeyboardMarkup:
    """ساخت کیبورد شیشه‌ای تغییر زبان همراه با تیک فعال روی زبان فعلی."""
    fa_label = "🇮🇷 فارسی " + ("✅" if current_lang == "fa" else "")
    en_label = "🇬🇧 English " + ("✅" if current_lang == "en" else "")

    buttons = [
        [
            InlineKeyboardButton(text=fa_label, callback_data="lang_fa"),
            InlineKeyboardButton(text=en_label, callback_data="lang_en"),
        ],
        [
            InlineKeyboardButton(
                text="❌ انصراف / Close" if current_lang == "en" else "❌ انصراف",
                callback_data="close_menu",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_support_inline_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    """ساخت کیبورد شیشه‌ای پشتیبانی بر اساس زبان کاربر."""
    channel_text = "📢 Channel" if lang == "en" else "📢 کانال اطلاع‌رسانی"
    support_text = "💬 Support" if lang == "en" else "💬 ارتباط با پشتیبانی"

    buttons = [
        [
            InlineKeyboardButton(text=channel_text, url="https://t.me/telegram"),
            InlineKeyboardButton(text=support_text, url="https://t.me/telegram"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)