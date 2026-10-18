from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from app.database.models.user import User
from app.database.repositories.order_repository import OrderRepository
from app.database.session import async_session_maker

router = Router()

STATUS_MAP = {
    "PENDING": "⏳ در انتظار پردازش",
    "SUBMITTED": "📨 ارسال‌شده به سرویس‌دهنده",
    "IN_PROGRESS": "⚡ در حال انجام",
    "COMPLETED": "✅ تکمیل‌شده",
    "PARTIAL": "◐ ناقص (مرجوعی متناسب)",
    "CANCELED": "❌ لغو شده",
    "FAILED": "⚠️ ناموفق (سکه بازگردانده شد)",
}


def _status_text(order) -> str:
    return STATUS_MAP.get(order.status.value, order.status.value)


@router.message(Command("my_orders"))
@router.message(F.text == "📋 پیگیری سفارش‌ها")
async def list_user_orders(message: Message, db_user: User):
    async with async_session_maker() as session:
        orders = await OrderRepository(session).get_user_orders(user_id=db_user.id, limit=10)
    if not orders:
        return await message.answer("شما هنوز هیچ سفارشی ثبت نکرده‌اید.")
    lines = ["📋 **لیست ۱۰ سفارش اخیر شما:**\n"]
    for o in orders:
        link_line = f"\n🔗 {o.target_link}" if o.target_link else ""
        lines.append(f"🆔 `{o.tracking_code}` | {_status_text(o)}{link_line}\n🔢 تعداد: {o.quantity:,} | 💰 هزینه: {o.cost_coins} سکه\n-------------------")
    await message.answer("\n".join(lines), parse_mode="Markdown")


@router.message(F.text.startswith("ORD-"))
async def track_order_by_code(message: Message, db_user: User):
    code = message.text.strip()
    async with async_session_maker() as session:
        order = await OrderRepository(session).get_by_tracking_code(code)
    if not order or order.user_id != db_user.id:
        return await message.answer("❌ سفارشی با این کد پیگیری یافت نشد.")
    link_line = f"🔗 **لینک:** `{order.target_link}`\n" if order.target_link else ""
    await message.answer(
        f"📦 **اطلاعات سفارش {order.tracking_code}**\n\n"
        f"{link_line}"
        f"🔹 **تعداد:** {order.quantity:,}\n"
        f"🔹 **هزینه:** {order.cost_coins} سکه\n"
        f"🔹 **وضعیت فعلی:** {_status_text(order)}",
        parse_mode="Markdown",
    )
