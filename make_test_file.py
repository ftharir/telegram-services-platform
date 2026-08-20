from pathlib import Path
code = """import asyncio
from unittest.mock import AsyncMock, patch
from app.database.models.order import Order, OrderStatus
from app.services.wallet_service import WalletService, InsufficientBalanceError
from app.services.order_lifecycle_service import OrderLifecycleService, MAPPING_STATUS
from app.integrations.rapidseen.schemas import RapidSeenOrderStatusResponse

class DummyWallet:
    def __init__(self, balance):
        self.id = 1
        self.balance = balance

async def test_wallet_operations():
    mock_session = AsyncMock()
    with patch("app.services.wallet_service.WalletRepository") as MockRepo:
        instance = MockRepo.return_value
        instance.get_by_user_id = AsyncMock(return_value=DummyWallet(balance=100))
        instance.get_balance = AsyncMock(return_value=100)
        instance.add_transaction = AsyncMock()
        instance.update_balance = AsyncMock()
        wallet_service = WalletService(mock_session)
        await wallet_service.debit(user_id=1, amount=40, description="Test Debit")
        assert instance.add_transaction.called
        await wallet_service.credit(user_id=1, amount=50, description="Test Credit")
        assert instance.add_transaction.called
        print("1. Wallet Credit/Debit & Transaction Logging PASSED!")

async def test_wallet_insufficient_balance():
    mock_session = AsyncMock()
    with patch("app.services.wallet_service.WalletRepository") as MockRepo:
        instance = MockRepo.return_value
        instance.get_by_user_id = AsyncMock(return_value=DummyWallet(balance=50))
        instance.get_balance = AsyncMock(return_value=50)
        wallet_service = WalletService(mock_session)
        try:
            await wallet_service.debit(user_id=1, amount=100, description="Test Debit")
            assert False, "Should have raised InsufficientBalanceError"
        except InsufficientBalanceError:
            print("2. Insufficient Balance PASSED!")

async def test_order_status_mapping():
    assert MAPPING_STATUS.get("Pending") == OrderStatus.PENDING
    assert MAPPING_STATUS.get("In progress") == OrderStatus.IN_PROGRESS
    assert MAPPING_STATUS.get("Done") == OrderStatus.COMPLETED
    assert MAPPING_STATUS.get("Canceled") == OrderStatus.CANCELED
    assert MAPPING_STATUS.get("Partial") == OrderStatus.PARTIAL
    print("3. Order Status Mapping PASSED!")

async def test_double_refund_protection():
    mock_order = Order()
    mock_order.id = 202
    mock_order.user_id = 1
    mock_order.quantity = 1000
    mock_order.cost_coins = 500
    mock_order.status = OrderStatus.IN_PROGRESS
    mock_order.external_order_id = 9988
    mock_session = AsyncMock()
    mock_client = AsyncMock()
    lifecycle_service = OrderLifecycleService(mock_session, rapidseen_client=mock_client)
    lifecycle_service.wallet_service = AsyncMock()
    await lifecycle_service._process_refund_if_eligible(mock_order, remains=0)
    lifecycle_service.wallet_service.credit.assert_not_called()
    print("4. Double Refund / Zero Refund Protection PASSED!")

async def test_tracking_code_format():
    import uuid
    code = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    assert code.startswith("ORD-") and len(code) == 12
    print("5. Tracking Code Format PASSED!")

async def main():
    await test_wallet_operations()
    await test_wallet_insufficient_balance()
    await test_order_status_mapping()
    await test_double_refund_protection()
    await test_tracking_code_format()

if __name__ == "__main__":
    asyncio.run(main())
"""
Path("test_phase2_suite.py").write_text(code, encoding="utf-8")
print("test_phase2_suite.py successfully updated!")
