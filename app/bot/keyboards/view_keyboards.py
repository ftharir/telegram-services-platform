from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_speed_keyboard(recent_speeds: list[str] = None) -> InlineKeyboardMarkup:
    buttons = []
    if recent_speeds:
        recent_row = [InlineKeyboardButton(text=f"⚡ {s}", callback_data=f"speed:{s}") for s in recent_speeds]
        buttons.append(recent_row)
    
    buttons.append([
        InlineKeyboardButton(text="عادی (Normal)", callback_data="speed:normal"),
        InlineKeyboardButton(text="سریع (Fast)", callback_data="speed:fast"),
        InlineKeyboardButton(text="فوری (Instant)", callback_data="speed:instant")
    ])
    buttons.append([InlineKeyboardButton(text="❌ لغو عملیات", callback_data="cancel_view_order")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ تأیید و ثبت سفارش", callback_data="confirm_view_order"),
                InlineKeyboardButton(text="❌ لغو", callback_data="cancel_view_order")
            ]
        ]
    )

def get_cancel_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ لغو عملیات")]],
        resize_keyboard=True
    )
