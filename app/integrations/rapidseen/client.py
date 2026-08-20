import httpx
from typing import Optional
from app.integrations.rapidseen.schemas import (
    RapidSeenAddOrderResponse,
    RapidSeenOrderStatusResponse,
    RapidSeenCancelOrderResponse,
)

class RapidSeenClient:
    def __init__(self, api_key: str, base_url: str = "https://rapidseen.com/api/v2"):
        self.api_key = api_key
        self.base_url = base_url

    async def add_order(self, service_id: int, link: str, quantity: int) -> RapidSeenAddOrderResponse:
        payload = {
            "key": self.api_key,
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(self.base_url, data=payload)
                data = response.json()
                return RapidSeenAddOrderResponse(**data)
            except Exception as e:
                return RapidSeenAddOrderResponse(error=str(e))

    async def get_status(self, order_id: int) -> RapidSeenOrderStatusResponse:
        payload = {
            "key": self.api_key,
            "action": "status",
            "order": order_id,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(self.base_url, data=payload)
                data = response.json()
                return RapidSeenOrderStatusResponse(**data)
            except Exception as e:
                return RapidSeenOrderStatusResponse(error=str(e))

    async def cancel_order(self, order_id: int) -> RapidSeenCancelOrderResponse:
        payload = {
            "key": self.api_key,
            "action": "cancel",
            "order": order_id,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(self.base_url, data=payload)
                data = response.json()
                return RapidSeenCancelOrderResponse(**data)
            except Exception as e:
                return RapidSeenCancelOrderResponse(error=str(e))
