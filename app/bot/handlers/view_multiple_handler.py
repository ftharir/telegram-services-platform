from uuid import uuid4

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.bot.states.view_states import ViewMultipleOrderStates
from app.bot.keyboards.view_keyboards import get_speed_keyboard, get_confirm_keyboard, get_cancel_reply_keyboard
from app.services.link_validator_service import LinkValidatorService
from app.services.wallet_service import WalletService, InsufficientBalanceError
from app.services.order_service import DuplicateOrderError
from app.services.order_placement_service import OrderPlacementService, OrderPlacementError
from app.integrations.rapidseen.client import RapidSeenClient
from app.database.models.user import User
from app.database.session import async_session_maker
from app.core.config import settings

router = Router()
MIN_VIEW_QTY = 100
MAX_VIEW_QTY = 100000
PRICE_PER_VIEW = settings.VIEW_PRICE_COINS_PER_100  # coins per 100 views
SERVICE_ID = settings.VIEW_SERVICE_ID

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
async def process_multi_posts(message: Message, state: FSMContext, db_user: User):
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
    await state.update_data(valid_links=valid_links, batch_key=uuid4().hex)
    await state.set_state(ViewMultipleOrderStates.CONFIRMING_ORDERS)
    data = await state.get_data()
    qty_per_post = data["quantity"]
    total_cost = len(valid_links) * ((qty_per_post // 100) * PRICE_PER_VIEW)
    async with async_session_maker() as session:
        ws = WalletService(session)
        balance = await ws.get_balance(db_user.id)
    remains = balance - total_cost
    summary = (f"📊 **نتیجه بررسی لینک‌ها:**\n{report_text}\n\n📋 **خلاصه سفارشات چندپستی**\n🔹 **تعداد پست‌های معتبر:** {len(valid_links)}\n🔹 **تعداد بازدید هر پست:** {qty_per_post:,}\n🔹 **سرعت:** {data["speed"]}\n💰 **هزینه کل:** {total_cost} سکه\n💳 **موجودی فعلی:** {balance} سکه\n💵 **موجودی پس از کسر:** {remains} سکه\n")
    if remains < 0:
        summary += "\n❌ **خطا:** موجودی سکه شما کافی نیست."
        await message.answer(summary, parse_mode="Markdown")
        await state.clear()
    else:
        await message.answer(summary, parse_mode="Markdown", reply_markup=get_confirm_keyboard())

@router.callback_query(ViewMultipleOrderStates.CONFIRMING_ORDERS, F.data == "confirm_view_order")
async def confirm_multi_view(callback: CallbackQuery, state: FSMContext, db_user: User):
    data = await state.get_data()
    qty_per_post = data["quantity"]
    valid_links = data["valid_links"]
    batch_key = data["batch_key"]
    cost_per_post = (qty_per_post // 100) * PRICE_PER_VIEW
    created_orders = []
    failed_links = []
    stopped_for_balance = False
    async with async_session_maker() as session:
        client = RapidSeenClient(api_key=settings.RAPIDSEEN_API_KEY, base_url=settings.RAPIDSEEN_API_URL)
        placement = OrderPlacementService(session, rapidseen_client=client)
        for idx, link in enumerate(valid_links):
            try:
                order = await placement.place_order(
                    user_id=db_user.id,
                    service_id=SERVICE_ID,
                    quantity=qty_per_post,
                    cost_coins=cost_per_post,
                    target_link=link,
                    idempotency_key=f"{batch_key}-{idx}",
                )
                await session.commit()
                created_orders.append((order, link))
            except InsufficientBalanceError:
                await session.rollback()
                stopped_for_balance = True
                failed_links.extend(valid_links[idx:])
                break
            except DuplicateOrderError:
                await session.rollback()  # this link of the batch was already registered
            except OrderPlacementError:
                await session.commit()  # keep the automatic refund and the FAILED status
                failed_links.append(link)
    if not created_orders:
        reason = "موجودی سکه شما کافی نیست." if stopped_for_balance else "ثبت سفارش‌ها نزد سرویس‌دهنده ناموفق بود (سکه‌ها بازگردانده شد)."
        await callback.message.edit_text(f"❌ هیچ سفارشی ثبت نشد. {reason}")
        await state.clear()
        return
    codes_text = "\n".join([f"• `{o.tracking_code}` ({link})" for o, link in created_orders])
    total_cost = len(created_orders) * cost_per_post
    text = (
        f"✅ **تعداد {len(created_orders)} سفارش با موفقیت ثبت شد!**\n\n"
        f"📋 **کدهای پیگیری:**\n{codes_text}\n\n💰 **هزینه کل کسرشده:** {total_cost} سکه"
    )
    if failed_links:
        text += f"\n\n⚠️ {len(failed_links)} لینک ثبت نشد (سکه‌ی آن‌ها کسر نشده یا بازگردانده شده است)."
    await callback.message.edit_text(text, parse_mode="Markdown")
    await state.clear()
