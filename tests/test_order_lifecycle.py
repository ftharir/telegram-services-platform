from unittest.mock import AsyncMock

from app.core.enums import OrderStatus, TransactionType
from app.database.models.order import Order
from app.integrations.rapidseen.schemas import RapidSeenCancelOrderResponse, RapidSeenOrderStatusResponse
from app.services.order_lifecycle_service import MAPPING_STATUS, OrderLifecycleService


def make_order(**kw):
    order = Order()
    order.id = kw.get("id", 1)
    order.user_id = 7
    order.service_id = 1
    order.quantity = kw.get("quantity", 1000)
    order.cost_coins = kw.get("cost_coins", 100)
    order.tracking_code = "ORD-20260101-ABCDE"
    order.rapidseen_order_id = kw.get("rapidseen_order_id", "554433")
    order.status = kw.get("status", OrderStatus.SUBMITTED)
    order.refunded_coins = 0
    return order


def make_service(orders, status_response):
    client = AsyncMock()
    client.get_status.return_value = status_response
    client.cancel_order.return_value = RapidSeenCancelOrderResponse(cancel="Sent")
    service = OrderLifecycleService(AsyncMock(), rapidseen_client=client)
    service.order_repo = AsyncMock()
    service.order_repo.get_open_orders.return_value = orders
    service.order_repo.get_by_id.return_value = orders[0] if orders else None
    service.wallet_service = AsyncMock()
    return service, client


def test_both_provider_spellings_of_completed_are_mapped():
    assert MAPPING_STATUS["Completed"] == OrderStatus.COMPLETED
    assert MAPPING_STATUS["Done"] == OrderStatus.COMPLETED
    assert MAPPING_STATUS["Processing"] == OrderStatus.IN_PROGRESS


async def test_status_is_read_with_the_numeric_provider_id():
    order = make_order()
    service, client = make_service([order], RapidSeenOrderStatusResponse(status="Completed", remains=0))
    await service.process_open_orders()
    client.get_status.assert_awaited_once_with(554433)
    assert order.status == OrderStatus.COMPLETED
    service.session.commit.assert_awaited_once()
    service.wallet_service.credit.assert_not_called()


async def test_partial_order_is_refunded_proportionally_once():
    order = make_order(quantity=1000, cost_coins=100)
    service, _ = make_service([order], RapidSeenOrderStatusResponse(status="Partial", remains=250))
    await service.process_open_orders()
    kwargs = service.wallet_service.credit.call_args.kwargs
    assert kwargs["amount"] == 25 and kwargs["transaction_type"] == TransactionType.REFUND
    assert order.refunded_coins == 25 and order.remains == 250 and order.status == OrderStatus.PARTIAL
    # a second pass over the same order must not pay again
    await service._process_refund_if_eligible(order, remains=250)
    assert service.wallet_service.credit.await_count == 1


async def test_canceled_order_without_remains_is_not_refunded():
    order = make_order()
    service, _ = make_service([order], RapidSeenOrderStatusResponse(status="Canceled"))
    await service.process_open_orders()
    service.wallet_service.credit.assert_not_called()
    assert order.status == OrderStatus.CANCELED and order.refunded_coins == 0


async def test_orders_without_a_usable_provider_id_are_skipped():
    orders = [make_order(id=1, rapidseen_order_id=None), make_order(id=2, rapidseen_order_id="abc")]
    service, client = make_service(orders, RapidSeenOrderStatusResponse(status="Completed", remains=0))
    await service.process_open_orders()
    client.get_status.assert_not_called()


async def test_cancel_request_uses_the_provider_id():
    order = make_order()
    service, client = make_service([order], RapidSeenOrderStatusResponse(status="Pending"))
    assert await service.request_cancel(order.id) == "Sent"
    client.cancel_order.assert_awaited_once_with(554433)
    order.rapidseen_order_id = None
    assert await service.request_cancel(order.id) == "Not possible"
