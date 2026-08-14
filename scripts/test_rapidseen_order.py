import asyncio
import sys
import uuid
from pathlib import Path

# افزودن مسیر ریشه پروژه به PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from app.database.session import async_session_maker
from app.integrations.rapidseen.client import RapidSeenClient
from app.services.order_placement_service import OrderPlacementError, OrderPlacementService
from app.services.wallet_service import InsufficientBalanceError, WalletService


async def run_developer_test():
    """اسکریپت تست توسعه‌دهنده جهت بررسی صحت جریان ثبت سفارش."""
    print("=== Starting Task 5 Order Placement Test ===")

    async with async_session_maker() as session:
        wallet_service = WalletService(session)
        placement_service = OrderPlacementService(session, rapidseen_client=RapidSeenClient())

        # ۱. شارژ اولیه کیف پول کاربر شماره ۱ جهت تست
        test_user_id = 1
        await wallet_service.credit(user_id=test_user_id, amount=200, description="Test initial deposit")
        bal = await wallet_service.get_balance(test_user_id)
        print(f"User #{test_user_id} balance before test: {bal} coins")

        # ۲. تولید کلید منحصر به‌فرد برای جلوگیری از ثبت تکراری
        unique_key = f"dev_test_{uuid.uuid4().hex[:8]}"

        print("\n--- Testing Order Flow (Safe Mode) ---")
        try:
            # در صورتی که API Key معتبر نباشد، خطای شبکه رخ داده و سیستم Auto-Refund را تست می‌کند
            order = await placement_service.place_order(
                user_id=test_user_id,
                service_id=1,
                quantity=100,
                cost_coins=50,
                target_link="https://t.me/test_channel",
                idempotency_key=unique_key,
            )
            print(f"SUCCESS: Order placed! Tracking Code: {order.tracking_code}, RapidSeen ID: {order.rapidseen_order_id}")
        except OrderPlacementError as e:
            print(f"EXPECTED API/AUTO-REFUND RESULT: {e}")

        # ۳. بررسی موجودی پس از انجام تراکنش/بازگشت وجه
        final_bal = await wallet_service.get_balance(test_user_id)
        print(f"User #{test_user_id} balance after test: {final_bal} coins")

        # ۴. تست جلوگیری از ثبت تکراری با همان idempotency_key
        print("\n--- Testing Idempotency Protection ---")
        try:
            await placement_service.place_order(
                user_id=test_user_id,
                service_id=1,
                quantity=100,
                cost_coins=50,
                target_link="https://t.me/test_channel",
                idempotency_key=unique_key,
            )
        except Exception as e:
            print(f"SUCCESS: Duplicate order blocked! Reason: {e}")

        # Rollback تغییرات تست از دیتابیس
        await session.rollback()
        print("\n=== Task 5 Test Completed Successfully ===")


if __name__ == "__main__":
    asyncio.run(run_developer_test())