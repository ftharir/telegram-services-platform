from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from app.database.models.order import Order
from app.integrations.rapidseen.schemas import RapidSeenAddOrderResponse
from app.services.order_placement_service import OrderPlacementService


def test_order_model_has_a_nullable_target_link_column():
    column = Order.__table__.c.target_link
    assert column.nullable is True
    assert column.type.length == 512


async def test_placement_stores_the_target_link_on_the_order():
    client = AsyncMock()
    client.add_order.return_value = RapidSeenAddOrderResponse(order=1001)
    service = OrderPlacementService(MagicMock(), rapidseen_client=client)
    service.order_repo.get_by_idempotency_key = AsyncMock(return_value=None)
    service.wallet_service.debit = AsyncMock()
    order = SimpleNamespace(tracking_code="ORD-20260101-ABCDE")
    service.order_service.create_internal_order = AsyncMock(return_value=order)
    service.order_service.update_order_status = AsyncMock()

    await service.place_order(
        user_id=1,
        service_id=1,
        quantity=100,
        cost_coins=1,
        target_link="https://t.me/some_channel/42",
        idempotency_key="key-1",
    )

    kwargs = service.order_service.create_internal_order.call_args.kwargs
    assert kwargs["target_link"] == "https://t.me/some_channel/42"
