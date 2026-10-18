from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from app.services.order_lifecycle_service import OrderLifecycleService
from app.database.session import async_session_maker

router = Router()

STATUS_MAP = {
    "PENDING": "⏳ در انتظار پردازش",
    "PROCESSING": "⚡ در حال ارسال",
    "COMPLETED": "✅ تکمیل‌شده",
    "CANCELLED": "❌ لغو شده"
}

@router.message(Command("my_orders"))
@router.message(F.text == "📋 پیگیری سفارش‌ها")
async def list_user_orders(message: Message):
    user_id = message.from_user.id
    async with async_session_maker() as session:
        lifecycle = OrderLifecycleService(session)
        orders = await lifecycle.get_user_orders(user_id=user_id, limit=10)
    if not orders:
        return await message.answer("شما هنوز هیچ سفارشی ثبت نکرده‌اید.")
    lines = ["📋 **لیست ۱۰ سفارش اخیر شما:**\n"]
    for o in orders:
        st = STATUS_MAP.get(str(o.status).upper(), str(o.status))
        lines.append(f"🆔 `{o.tracking_code}` | {st}\n🔗 {o.target_link}\n🔢 تعداد: {o.quantity:,} | 💰 هزینه: {o.cost} سکه\n-------------------")
    await message.answer("\n".join(lines), parse_mode="Markdown")

@router.message(F.text.startswith("ORD-"))
async def track_order_by_code(message: Message):
    code = message.text.strip()
    async with async_session_maker() as session:
        lifecycle = OrderLifecycleService(session)
        order = await lifecycle.get_by_tracking_code(code)
        if not order:
            return await message.answer("❌ سفارشی با این کد پیگیری یافت نشد.")
        st = STATUS_MAP.get(str(order.status).upper(), str(order.status))
        await message.answer(
            f"📦 **اطلاعات سفارش {order.tracking_code}**\n\n"
            f"🔹 **نوع:** {order.service_type}\n"
            f"🔹 **تعداد:** {order.quantity:,}\n"
            f"🔹 **وضعیت فعلی:** {st}\n"
            f"🔗 **لینک:** `{order.target_link}`",
            parse_mode="Markdown"
        )
