from typing import Dict

MESSAGES: Dict[str, Dict[str, str]] = {
    "fa": {
        "welcome": "سلام <b>{name}</b> عزیز! 👋\n\nبه <b>پلتفرم خدمات تلگرام</b> خوش آمدید.\nاز منوی زیر می‌توانید به تمامی سرویس‌ها و امکانات ربات دسترسی داشته باشید.",
        "profile": "👤 <b>پروفایل کاربری شما</b>\n\n🆔 <b>شناسه تلگرام:</b> <code>{telegram_id}</code>\n👤 <b>نام:</b> {first_name}\nنام کاربری: @{username}\n🌐 <b>زبان انتخاب شده:</b> {language}\n📅 <b>تاریخ عضویت:</b> <code>{created_at}</code>",
        "settings": "⚙️ <b>بخش تنظیمات</b>\nلطفاً گزینه مورد نظر خود را انتخاب کنید:",
        "help": "❓ <b>راهنما و پشتیبانی</b>\n\nاین ربات یک پلتفرم جامع برای ارائه خدمات هوشمند در تلگرام است.\nدر صورت بروز هرگونه مشکل یا داشتن سوال می‌توانید با تیم پشتیبانی ما در ارتباط باشید.",
        "services": "🛠️ <b>لیست سرویس‌های فعال:</b>\n\n۱. سرویس پردازش هوشمند پیام‌ها 🤖\n۲. سرویس مدیریت حافظه و کارهای کاربر 📝\n\n<i>(سرویس‌های جدید به‌زودی اضافه خواهند شد...)</i>",
        "lang_changed": "✅ زبان شما با موفقیت به <b>فارسی</b> تغییر یافت.",
        "lang_already_active": "زبان انتخابی شما از قبل فعال است!",
        "btn_services": "🛠️ سرویس‌ها",
        "btn_profile": "👤 حساب کاربری",
        "btn_settings": "⚙️ تنظیمات",
        "btn_help": "❓ راهنما و پشتیبانی",
    },
    "en": {
        "welcome": "Hello <b>{name}</b>! 👋\n\nWelcome to the <b>Telegram Services Platform</b>.\nUse the menu below to access all bot features and services.",
        "profile": "👤 <b>User Profile</b>\n\n🆔 <b>Telegram ID:</b> <code>{telegram_id}</code>\n👤 <b>Name:</b> {first_name}\nUsername: @{username}\n🌐 <b>Language:</b> {language}\n📅 <b>Joined:</b> <code>{created_at}</code>",
        "settings": "⚙️ <b>Settings</b>\nPlease select an option:",
        "help": "❓ <b>Help & Support</b>\n\nThis bot is a comprehensive platform for intelligent Telegram services.\nFeel free to contact support if you have any questions.",
        "services": "🛠️ <b>Active Services:</b>\n\n1. AI Message Processing 🤖\n2. Task & Memory Manager 📝\n\n<i>(New services coming soon...)</i>",
        "lang_changed": "✅ Your language has been successfully changed to <b>English</b>.",
        "lang_already_active": "Selected language is already active!",
        "btn_services": "🛠️ Services",
        "btn_profile": "👤 Profile",
        "btn_settings": "⚙️ Settings",
        "btn_help": "❓ Help & Support",
    },
}


def get_text(key: str, lang: str = "fa", **kwargs) -> str:
    """دریافت متن ترجمه‌شده بر اساس کلید و کد زبان کاربر."""
    lang_dict = MESSAGES.get(lang, MESSAGES["fa"])
    text = lang_dict.get(key, MESSAGES["fa"].get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text
