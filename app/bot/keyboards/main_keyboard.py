from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👁 ثبت بازدید (View)"), KeyboardButton(text="👁👁 ثبت بازدید چندپستی (View Multiple)")],
            [KeyboardButton(text="📋 پیگیری سفارش‌ها"), KeyboardButton(text="💰 کیف پول / حساب کاربری")]
        ],
        resize_keyboard=True
    )
