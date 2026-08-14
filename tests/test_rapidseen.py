import asyncio
from app.integrations.rapidseen.client import RapidSeenClient, RapidSeenAPIError

async def test():
    client = RapidSeenClient(api_key="dummy_key_for_test")
    print("RapidSeen client initialized successfully!")
    assert client.base_url != ""
    print("Task 4 client structure test PASSED!")

if __name__ == "__main__":
    asyncio.run(test())
