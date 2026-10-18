from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.bot.states.view_states import ViewOrderStates
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

@router.message(F.text == "👁 ثبت بازدید (View)")
async def start_single_view(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(ViewOrderStates.WAITING_FOR_QUANTITY)
    await message.answer(f"لطفاً تعداد بازدید مورد نظر خود را وارد کنید (حداقل {MIN_VIEW_QTY} و حداکثر {MAX_VIEW_QTY}):", reply_markup=get_cancel_reply_keyboard())

@router.message(ViewOrderStates.WAITING_FOR_QUANTITY)
async def process_quantity(message: Message, state: FSMContext):
    if message.text == "❌ لغو عملیات":
        await state.clear()
        return await message.answer("عملیات لغو شد.", reply_markup=None)
    if not message.text.isdigit():
        return await message.answer("لطفاً یک عدد معتبر وارد کنید:")
    qty = int(message.text)
    if qty < MIN_VIEW_QTY or qty > MAX_VIEW_QTY:
        return await message.answer(f"تعداد باید بین {MIN_VIEW_QTY} تا {MAX_VIEW_QTY} باشد. دوباره وارد کنید:")
    await state.update_data(quantity=qty)
    await state.set_state(ViewOrderStates.WAITING_FOR_SPEED)
    data = await state.get_data()
    recent_speeds = data.get("recent_speeds", [])
    await message.answer("لطفاً سرعت ارسال بازدید را انتخاب کنید:", reply_markup=get_speed_keyboard(recent_speeds))

@router.callback_query(ViewOrderStates.WAITING_FOR_SPEED, F.data.startswith("speed:"))
async def process_speed(callback: CallbackQuery, state: FSMContext):
    speed = callback.data.split(":")[1]
    data = await state.get_data()
    recent = data.get("recent_speeds", [])
    if speed not in recent:
        recent.insert(0, speed)
        recent = recent[:2]
    await state.update_data(speed=speed, recent_speeds=recent)
    await state.set_state(ViewOrderStates.WAITING_FOR_POST)
    await callback.message.edit_text(f"سرعت «{speed}» انتخاب شد.")
    await callback.message.answer("اکنون لینک پست یا خود پست را ارسال/فوروارد کنید:")

@router.message(ViewOrderStates.WAITING_FOR_POST)
async def process_post_link(message: Message, state: FSMContext):
    if message.text == "❌ لغو عملیات":
        await state.clear()
        return await message.answer("عملیات لغو شد.")
    raw_link = message.text or ""
    if message.forward_from_chat and message.forward_from_chat.username:
        raw_link = f"https://t.me/{message.forward_from_chat.username}/{message.forward_from_message_id}"
    validation = LinkValidatorService.validate_telegram_post_link(raw_link)
    if not validation["is_valid"]:
        return await message.answer(f"❌ {validation["error"]}\nلطفاً لینک صحیح را وارد کنید:")
    await state.update_data(target_link=validation["final_link"])
    await state.set_state(ViewOrderStates.CONFIRMING_ORDER)
    data = await state.get_data()
    qty = data["quantity"]
    cost = (qty // 100) * PRICE_PER_VIEW
    async with async_session_maker() as session:
        ws = WalletService(session)
        balance = await ws.get_balance(message.from_user.id)
    remains = balance - cost
    summary_text = (f"📋 **خلاصه سفارش بازدید**\n\n🔹 **نوع سرویس:** بازدید تک‌پستی (View)\n🔹 **تعداد بازدید:** {qty:,}\n🔹 **سرعت انتخاب‌شده:** {data["speed"]}\n🔗 **لینک پست:** `{validation["final_link"]}`\n\n💰 **هزینه سفارش:** {cost} سکه\n💳 **موجودی فعلی شما:** {balance} سکه\n💵 **موجودی پس از کسر:** {remains} سکه\n")
    if remains < 0:
        summary_text += "\n❌ **خطا:** موجودی سکه شما برای ثبت این سفارش کافی نیست."
        await message.answer(summary_text, parse_mode="Markdown")
        await state.clear()
    else:
        await message.answer(summary_text, parse_mode="Markdown", reply_markup=get_confirm_keyboard())

@router.callback_query(F.data == "cancel_view_order")
async def cancel_order_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ عملیات سفارش لغو شد.")

@router.callback_query(ViewOrderStates.CONFIRMING_ORDER, F.data == "confirm_view_order")
async def confirm_single_view(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    qty = data["quantity"]
    cost = (qty // 100) * PRICE_PER_VIEW
    link = data["target_link"]
    user_id = callback.from_user.id
    async with async_session_maker() as session:
        ws = WalletService(session)
        lifecycle = OrderLifecycleService(session)
        try:
            await ws.debit(user_id=user_id, amount=cost, description=f"ثبت سفارش بازدید برای {link}")
        except InsufficientBalanceError:
            await callback.message.edit_text("❌ موجودی سکه شما برای این سفارش کافی نیست.")
            await state.clear()
            return
        order = await lifecycle.create_order(user_id=user_id, service_type="VIEW", quantity=qty, cost=cost, target_link=link)
        await session.commit()
    client = RapidSeenClient()
    await client.add_order(service_id=1, link=link, quantity=qty)  # FALLBACK service_id=1
    await callback.message.edit_text(f"✅ **سفارش شما با موفقیت ثبت شد!**\n\n🆔 **کد پیگیری:** `{order.tracking_code}`\n🔗 **لینک:** `{link}`\n🔢 **تعداد:** {qty:,}\n💰 **هزینه:** {cost} سکه\n\nسفارش شما در جریان پردازش قرار گرفت.", parse_mode="Markdown")
    await state.clear()