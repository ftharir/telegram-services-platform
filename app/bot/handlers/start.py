from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.database.models.user import User
from app.services.user_service import UserService
from app.bot.keyboards import (
    get_main_menu_keyboard,
    get_settings_inline_keyboard,
    get_support_inline_keyboard,
)

router = Router(name="main_router")


@router.message(CommandStart())
async def command_start_handler(message: Message, db_user: User) -> None:
    """هندلر دستور /start - نمایش پیام خوش‌آمدگویی و فعال‌سازی کیبورد منوی اصلی."""
    welcome_text = (
        f"سلام <b>{db_user.first_name}</b> عزیز! 👋\n\n"
        "به <b>پلتفرم خدمات تلگرام</b> خوش آمدید.\n"
        "از منوی زیر می‌توانید به تمامی سرویس‌ها و امکانات ربات دسترسی داشته باشید."
    )
    await message.answer(
        text=welcome_text,
        reply_markup=get_main_menu_keyboard(),
    )


@router.message(F.text == "👤 حساب کاربری")
async def user_profile_handler(message: Message, db_user: User) -> None:
    """نمایش مشخصات کاربر بر اساس داده‌های موجود در دیتابیس PostgreSQL."""
    created_at_str = db_user.created_at.strftime("%Y-%m-%d %H:%M") if db_user.created_at else "نامشخص"
    
    profile_text = (
        "👤 <b>پروفایل کاربری شما</b>\n\n"
        f"🆔 <b>شناسه تلگرام:</b> <code>{db_user.telegram_id}</code>\n"
        f"👤 <b>نام:</b> {db_user.first_name}\n"
        f"نام کاربری: @{db_user.username or 'ثبت نشده'}\n"
        f"🌐 <b>زبان انتخاب شده:</b> {db_user.language_code}\n"
        f"📅 <b>تاریخ عضویت:</b> <code>{created_at_str}</code>"
    )
    await message.answer(text=profile_text)


@router.message(F.text == "⚙️ تنظیمات")
async def settings_handler(message: Message) -> None:
    """نمایش منوی تنظیمات با دکمه‌های Inline."""
    await message.answer(
        text="⚙️ <b>بخش تنظیمات</b>\nلطفاً گزینه مورد نظر خود را انتخاب کنید:",
        reply_markup=get_settings_inline_keyboard(),
    )


@router.message(F.text == "❓ راهنما و پشتیبانی")
async def support_handler(message: Message) -> None:
    """نمایش راهنما و دکمه‌های ارتباط با پشتیبانی."""
    help_text = (
        "❓ <b>راهنما و پشتیبانی</b>\n\n"
        "این ربات یک پلتفرم جامع برای ارائه خدمات هوشمند در تلگرام است.\n"
        "در صورت بروز هرگونه مشکل یا داشتن سوال می‌توانید با تیم پشتیبانی ما در ارتباط باشید."
    )
    await message.answer(
        text=help_text,
        reply_markup=get_support_inline_keyboard(),
    )


@router.message(F.text == "🛠️ سرویس‌ها")
async def services_handler(message: Message) -> None:
    """نمایش لیست سرویس‌های ربات (پیش‌زمینه فازهای بعدی)."""
    await message.answer(
        text="🛠️ <b>لیست سرویس‌های فعال:</b>\n\n"
             "۱. سرویس پردازش هوشمند پیام‌ها 🤖\n"
             "۲. سرویس مدیریت حافظه و کارهای کاربر 📝\n\n"
             "<i>(سرویس‌های جدید به‌زودی اضافه خواهند شد...)</i>"
    )


# --- Callback Query Handlers (دکمه‌های شیشه‌ای) ---

@router.callback_query(F.data.startswith("lang_"))
async def change_language_callback(
    callback: CallbackQuery,
    user_service: UserService,
    db_user: User,
) -> None:
    """تغییر زبان کاربر هنگام کلیک روی دکمه‌های Inline زبان."""
    new_lang = callback.data.split("_")[1]
    
    if db_user.language_code == new_lang:
        await callback.answer(text="زبان انتخابی شما از قبل فعال است!", show_alert=True)
        return

    await user_service.change_user_language(db_user.telegram_id, new_lang)
    lang_name = "فارسی" if new_lang == "fa" else "English"
    
    await callback.answer(text=f"زبان با موفقیت به {lang_name} تغییر یافت.", show_alert=True)
    if callback.message:
        await callback.message.edit_text(text=f"✅ زبان جدید شما: <b>{lang_name}</b>")


@router.callback_query(F.data == "close_menu")
async def close_menu_callback(callback: CallbackQuery) -> None:
    """حذف پیام حاوی منوی Inline."""
    if callback.message:
        await callback.message.delete()
    await callback.answer()