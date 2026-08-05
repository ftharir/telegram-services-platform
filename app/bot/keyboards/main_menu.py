from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """ساخت و بازگرداندن کیبورد اصلی ربات که زیر کادر چت قرار می‌گیرد."""
    keyboard = [
        [
            KeyboardButton(text="🛠️ سرویس‌ها"),
            KeyboardButton(text="👤 حساب کاربری"),
        ],
        [
            KeyboardButton(text="⚙️ تنظیمات"),
            KeyboardButton(text="❓ راهنما و پشتیبانی"),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,  # کوچک و متناسب‌سازی اندازه دکمه‌ها با صفحه گوشی
        persistent=True,       # باقی ماندن کیبورد روی صفحه
    )