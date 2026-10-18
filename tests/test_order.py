import asyncio
from app.database.session import async_session_maker
from app.services.order_service import OrderService, DuplicateOrderError
from tests.conftest import make_user

async def test():
    async with async_session_maker() as session:
        user = await make_user(session)
        service = OrderService(session)
        order = await service.create_internal_order(
            user_id=user.id,
            idempotency_key="test_key_123",
            service_id=101,
            quantity=1000,
            cost_coins=50,
        )
        print("Created Order Tracking Code:", order.tracking_code)
        try:
            await service.create_internal_order(
                user_id=user.id,
                idempotency_key="test_key_123",
                service_id=101,
                quantity=1000,
                cost_coins=50,
            )
        except DuplicateOrderError:
            print("Duplicate order protection test PASSED!")
        await session.rollback()

if __name__ == "__main__":
    asyncio.run(test())
