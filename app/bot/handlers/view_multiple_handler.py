from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.bot.states.view_states import ViewMultipleOrderStates
from app.bot.keyboards.view_keyboards import get_speed_keyboard, get_confirm_keyboard, get_cancel_reply_keyboard
from app.services.link_validator_service import LinkValidatorService
from app.services.wallet_service import WalletService
from app.services.order_lifecycle_service import OrderLifecycleService
from app.services.rapidseen_client import RapidSeenClient
from app.database.session import async_session_maker
from app.core.exceptions import InsufficientBalanceError

router = Router()
MIN_VIEW_QTY = 100
MAX_VIEW_QTY = 100000
PRICE_PER_VIEW = 1

@router.message(F.text == "👁👁 ثبت بازدید چندپستی (View Multiple)")
async def start_multiple_view(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(ViewMultipleOrderStates.WAITING_FOR_QUANTITY)
    await message.answer(f"لطفاً تعداد بازدید برای **هر پست** را وارد کنید (بین {MIN_VIEW_QTY} تا {MAX_VIEW_QTY}):", reply_markup=get_cancel_reply_keyboard())

@router.message(ViewMultipleOrderStates.WAITING_FOR_QUANTITY)
async def process_multi_quantity(message: Message, state: FSMContext):
    if message.text == "❌ لغو عملیات":
        await state.clear()
        return await message.answer("عملیات لغو شد.")
    if not message.text.isdigit():
        return await message.answer("لطفاً عدد معتبر وارد کنید:")
    qty = int(message.text)
    if qty < MIN_VIEW_QTY or qty > MAX_VIEW_QTY:
        return await message.answer(f"تعداد باید بین {MIN_VIEW_QTY} تا {MAX_VIEW_QTY} باشد:")
    await state.update_data(quantity=qty)
    await state.set_state(ViewMultipleOrderStates.WAITING_FOR_SPEED)
    data = await state.get_data()
    recent = data.get("recent_speeds", [])
    await message.answer("سرعت ارسال را انتخاب کنید:", reply_markup=get_speed_keyboard(recent))

@router.callback_query(ViewMultipleOrderStates.WAITING_FOR_SPEED, F.data.startswith("speed:"))
async def process_multi_speed(callback: CallbackQuery, state: FSMContext):
    speed = callback.data.split(":")[1]
    await state.update_data(speed=speed)
    await state.set_state(ViewMultipleOrderStates.WAITING_FOR_POSTS)
    await callback.message.edit_text(f"سرعت «{speed}» انتخاب شد.")
    await callback.message.answer("لطفاً لینک پست‌ها را ارسال کنید (حداکثر ۱۰ لینک در یک پیام، هر لینک در یک خط):")

@router.message(ViewMultipleOrderStates.WAITING_FOR_POSTS)
async def process_multi_posts(message: Message, state: FSMContext):
    if message.text == "❌ لغو عملیات":
        await state.clear()
        return await message.answer("عملیات لغو شد.")
    lines = [line.strip() for line in (message.text or "").split("\n") if line.strip()]
    if not lines:
        return await message.answer("هیچ لینکی دریافت نشد.")
    if len(lines) > 10:
        return await message.answer("❌ تعداد لینک‌ها در یک پیام نباید بیشتر از ۱۰ عدد باشد.")
    valid_links = []
    report_lines = []
    for idx, line in enumerate(lines, 1):
        res = LinkValidatorService.validate_telegram_post_link(line)
        if res["is_valid"]:
            valid_links.append(res["final_link"])
            report_lines.append(f"✅ لینک شماره {idx}: معتبر")
        else:
            report_lines.append(f"❌ لینک شماره {idx}: نامعتبر ({res["error"]})")
    report_text = "\n".join(report_lines)
    if not valid_links:
        return await message.answer(f"نتایج بررسی لینک‌ها:\n{report_text}\n\n❌ هیچ لینک معتبری یافت نشد. لطفاً لینک‌های صحیح را مجدداً ارسال کنید:")
    await state.update_data(valid_links=valid_links)
    await state.set_state(ViewMultipleOrderStates.CONFIRMING_ORDERS)
    data = await state.get_data()
    qty_per_post = data["quantity"]
    total_cost = len(valid_links) * ((qty_per_post // 100) * PRICE_PER_VIEW)
    async with async_session_maker() as session:
        ws = WalletService(session)
        balance = await ws.get_balance(message.from_user.id)
    remains = balance - total_cost
    summary = (f"📊 **نتیجه بررسی لینک‌ها:**\n{report_text}\n\n📋 **خلاصه سفارشات چندپستی**\n🔹 **تعداد پست‌های معتبر:** {len(valid_links)}\n🔹 **تعداد بازدید هر پست:** {qty_per_post:,}\n🔹 **سرعت:** {data["speed"]}\n💰 **هزینه کل:** {total_cost} سکه\n💳 **موجودی فعلی:** {balance} سکه\n💵 **موجودی پس از کسر:** {remains} سکه\n")
    if remains < 0:
        summary += "\n❌ **خطا:** موجودی سکه شما کافی نیست."
        await message.answer(summary, parse_mode="Markdown")
        await state.clear()
    else:
        await message.answer(summary, parse_mode="Markdown", reply_markup=get_confirm_keyboard())

@router.callback_query(ViewMultipleOrderStates.CONFIRMING_ORDERS, F.data == "confirm_view_order")
async def confirm_multi_view(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    qty_per_post = data["quantity"]
    valid_links = data["valid_links"]
    total_cost = len(valid_links) * ((qty_per_post // 100) * PRICE_PER_VIEW)
    user_id = callback.from_user.id
    created_orders = []
    async with async_session_maker() as session:
        ws = WalletService(session)
        lifecycle = OrderLifecycleService(session)
        try:
            await ws.debit(user_id=user_id, amount=total_cost, description=f"ثبت سفارش بازدید چندپستی ({len(valid_links)} پست)")
        except InsufficientBalanceError:
            await callback.message.edit_text("❌ موجودی سکه شما برای این سفارشات کافی نیست.")
            await state.clear()
            return
        for link in valid_links:
            order = await lifecycle.create_order(user_id=user_id, service_type="VIEW_MULTIPLE", quantity=qty_per_post, cost=(qty_per_post // 100) * PRICE_PER_VIEW, target_link=link)
            created_orders.append(order)
        await session.commit()
    client = RapidSeenClient()
    for link in valid_links:
        await client.add_order(service_id=1, link=link, quantity=qty_per_post)  # FALLBACK service_id=1
    codes_text = "\n".join([f"• `{o.tracking_code}` ({o.target_link})" for o in created_orders])
    await callback.message.edit_text(f"✅ **تعداد {len(created_orders)} سفارش با موفقیت ثبت شد!**\n\n📋 **کدهای پیگیری:**\n{codes_text}\n\n💰 **هزینه کل کسرشده:** {total_cost} سکه", parse_mode="Markdown")
    await state.clear()