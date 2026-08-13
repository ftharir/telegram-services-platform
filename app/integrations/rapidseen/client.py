from typing import Dict, List, Optional, Union
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.rapidseen.schemas import (
    RapidSeenAddOrderRequest,
    RapidSeenAddOrderResponse,
    RapidSeenBalanceResponse,
    RapidSeenOrderStatusResponse,
)

logger = get_logger(__name__)


class RapidSeenAPIError(Exception):
    """خطای عمومی در ارتباط با API خارجی."""
    pass


class RapidSeenClient:
    """کلاینت HTTP Async برای ارتباط با API سرویس‌دهنده RapidSeen."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 15.0,
    ) -> None:
        self.api_key = api_key or settings.RAPIDSEEN_API_KEY
        self.base_url = base_url or settings.RAPIDSEEN_API_URL
        self.timeout = timeout

    async def _post(self, data: dict) -> dict:
        """ارسال درخواست HTTP POST به API."""
        data["key"] = self.api_key
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(self.base_url, data=data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error("RapidSeen HTTP Status Error: %s", str(e))
                raise RapidSeenAPIError(f"HTTP Error from RapidSeen API: {e.response.status_code}") from e
            except httpx.RequestError as e:
                logger.error("RapidSeen Network/Request Error: %s", str(e))
                raise RapidSeenAPIError("Network connection error with RapidSeen API") from e

    async def add_order(
        self, service_id: int, link: str, quantity: int
    ) -> RapidSeenAddOrderResponse:
        """ارسال درخواست ثبت سفارش به API."""
        payload = RapidSeenAddOrderRequest(
            key=self.api_key,
            action="add",
            service=service_id,
            link=link,
            quantity=quantity,
        ).model_dump()

        res_data = await self._post(payload)
        return RapidSeenAddOrderResponse(**res_data)

    async def get_order_status(self, order_id: Union[int, str]) -> RapidSeenOrderStatusResponse:
        """دریافت وضعیت یک سفارش با ID."""
        payload = {"action": "status", "order": str(order_id)}
        res_data = await self._post(payload)
        return RapidSeenOrderStatusResponse(**res_data)

    async def get_multiple_order_statuses(
        self, order_ids: List[Union[int, str]]
    ) -> Dict[str, RapidSeenOrderStatusResponse]:
        """دریافت وضعیت گروهی چند سفارش."""
        orders_str = ",".join(str(oid) for oid in order_ids)
        payload = {"action": "status", "orders": orders_str}
        res_data = await self._post(payload)

        result = {}
        if isinstance(res_data, dict):
            for oid, info in res_data.items():
                if isinstance(info, dict):
                    result[str(oid)] = RapidSeenOrderStatusResponse(**info)
        return result

    async def get_account_balance(self) -> RapidSeenBalanceResponse:
        """استعلام موجودی حساب مدیریت در RapidSeen."""
        payload = {"action": "balance"}
        res_data = await self._post(payload)
        return RapidSeenBalanceResponse(**res_data)