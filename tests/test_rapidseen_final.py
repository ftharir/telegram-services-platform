import asyncio
from unittest.mock import AsyncMock, patch
from app.integrations.rapidseen.client import RapidSeenClient, RapidSeenAPIError

async def test():
    client = RapidSeenClient(api_key="test_key_123")
    
    # Mock successful add_order
    with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = {"order": 884422}
        res = await client.add_order(service_id=10, link="https://t.me/test", quantity=100)
        assert res.order == 884422
        print("Add order mock test PASSED!")

        # Mock status check
        mock_post.return_value = {"status": "Completed", "remains": "0"}
        status_res = await client.get_order_status(884422)
        assert status_res.status == "Completed"
        print("Get status mock test PASSED!")

        # Mock balance
        mock_post.return_value = {"balance": "50.25", "currency": "USD"}
        bal_res = await client.get_account_balance()
        assert bal_res.balance == "50.25"
        print("Get balance mock test PASSED!")

if __name__ == "__main__":
    asyncio.run(test())
