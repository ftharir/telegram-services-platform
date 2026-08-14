import asyncio
from unittest.mock import AsyncMock
from app.database.session import async_session_maker
from app.database.repositories.user_repository import UserRepository
from app.database.models.user import User
from app.services.wallet_service import WalletService
from app.services.order_placement_service import OrderPlacementService, OrderPlacementError
from app.integrations.rapidseen.schemas import RapidSeenAddOrderResponse

async def test():
    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        # دریافت کاربر تست
        user = await user_repo.get_by_telegram_id(99999999)
        if not user:
            # مقداردهی first_name برای جلوگیری از NotNullViolationError
            user = User(telegram_id=99999999, username="test_user_task5", first_name="TestUser")
            session.add(user)
            await session.flush()
            await session.refresh(user)
        user_id = user.id

        wallet_service = WalletService(session)
        await wallet_service.credit(user_id=user_id, amount=100)

        mock_client = AsyncMock()
        mock_client.add_order.return_value = RapidSeenAddOrderResponse(order=778899)

        placement_service = OrderPlacementService(session, rapidseen_client=mock_client)
        order = await placement_service.place_order(
            user_id=user_id,
            service_id=5,
            quantity=500,
            cost_coins=40,
            target_link="https://t.me/test_channel",
            idempotency_key="unit_key_1001",
        )
        print("1. Successful placement tracking code:", order.tracking_code)
        bal = await wallet_service.get_balance(user_id)
        assert bal == 60
        print("2. Debit balance test PASSED! New balance:", bal)

        mock_client.add_order.return_value = RapidSeenAddOrderResponse(error="Service Disabled")
        try:
            await placement_service.place_order(
                user_id=user_id,
                service_id=5,
                quantity=500,
                cost_coins=40,
                target_link="https://t.me/test_channel",
                idempotency_key="unit_key_1002",
            )
        except OrderPlacementError:
            print("3. Auto-refund on API Error PASSED!")

        bal_refund = await wallet_service.get_balance(user_id)
        assert bal_refund == 60
        print("4. Balance restored after refund PASSED! Balance:", bal_refund)

        await session.rollback()

if __name__ == "__main__":
    asyncio.run(test())