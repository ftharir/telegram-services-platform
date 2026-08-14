from typing import Dict, List, Optional, Union
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.rapidseen.schemas import (
    RapidSeenAddOrderResponse,
    RapidSeenBalanceResponse,
    RapidSeenCancelOrderResponse,
    RapidSeenOrderStatusResponse,
)

logger = get_logger(__name__)


class RapidSeenAPIError(Exception):
    """خطای اختصاصی مربوط به ارتباط یا پاسخ RapidSeen API."""
    pass


class RapidSeenClient:
    """
    HTTP Client اختصاصی جهت ارتباط با RapidSeen API.
    مسئولیت این کلاس فقط ارسال درخواست‌های HTTP و دریافت پاسخ‌های خامی است که به Pydantic Schemas تبدیل می‌شوند.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 15.0,
    ) -> None:
        self.api_key = api_key or settings.RAPIDSEEN_API_KEY
        self.base_url = base_url or settings.RAPIDSEEN_API_URL or "https://rapidseen.net/api/v2"
        self.timeout = timeout

    async def _post(self, data: dict) -> Union[dict, list]:
        """ارسال درخواست HTTP POST و مدیریت کامل خطاهای شبکه و HTTP."""
        if not self.api_key:
            raise RapidSeenAPIError("RAPIDSEEN_API_KEY is not configured in settings or .env")

        data["key"] = self.api_key
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                logger.debug("Sending POST request to RapidSeen API with action: %s", data.get("action"))
                response = await client.post(self.base_url, data=data)
                response.raise_for_status()

                json_resp = response.json()
                return json_resp

            except httpx.HTTPStatusError as e:
                logger.error("RapidSeen HTTP error status=%s, body=%s", e.response.status_code, e.response.text)
                raise RapidSeenAPIError(f"HTTP Error {e.response.status_code} from RapidSeen API") from e
            except httpx.TimeoutException as e:
                logger.error("RapidSeen API request timed out after %s seconds", self.timeout)
                raise RapidSeenAPIError("Connection to RapidSeen API timed out") from e
            except httpx.RequestError as e:
                logger.error("RapidSeen API network error: %s", str(e))
                raise RapidSeenAPIError("Network connection error with RapidSeen API") from e
            except ValueError as e:
                logger.error("Invalid JSON response received from RapidSeen API")
                raise RapidSeenAPIError("Invalid non-JSON response from RapidSeen API") from e

    async def add_order(
        self, service_id: int, link: str, quantity: int
    ) -> RapidSeenAddOrderResponse:
        """ثبت سفارش جدید در RapidSeen."""
        payload = {
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity,
        }
        res_data = await self._post(payload)
        if isinstance(res_data, dict):
            return RapidSeenAddOrderResponse(**res_data)
        raise RapidSeenAPIError("Unexpected response format for add_order")

    async def get_order_status(self, order_id: Union[int, str]) -> RapidSeenOrderStatusResponse:
        """دریافت وضعیت یک سفارش با ID."""
        payload = {"action": "status", "order": str(order_id)}
        res_data = await self._post(payload)
        if isinstance(res_data, dict):
            return RapidSeenOrderStatusResponse(**res_data)
        raise RapidSeenAPIError("Unexpected response format for get_order_status")

    async def get_multiple_order_statuses(
        self, order_ids: List[Union[int, str]]
    ) -> Dict[str, RapidSeenOrderStatusResponse]:
        """دریافت وضعیت گروهی چند سفارش (ارسال IDها با ویرگول)."""
        orders_str = ",".join(str(oid) for oid in order_ids)
        payload = {"action": "status", "orders": orders_str}
        res_data = await self._post(payload)

        result: Dict[str, RapidSeenOrderStatusResponse] = {}
        if isinstance(res_data, dict):
            for oid, info in res_data.items():
                if isinstance(info, dict):
                    result[str(oid)] = RapidSeenOrderStatusResponse(**info)
        return result

    async def cancel_orders(
        self, order_ids: List[Union[int, str]]
    ) -> List[RapidSeenCancelOrderResponse]:
        """ارسال درخواست لغو برای یک یا چند سفارش."""
        orders_str = ",".join(str(oid) for oid in order_ids)
        payload = {"action": "cancel", "orders": orders_str}
        res_data = await self._post(payload)

        result = []
        if isinstance(res_data, list):
            for item in res_data:
                if isinstance(item, dict):
                    result.append(RapidSeenCancelOrderResponse(**item))
        elif isinstance(res_data, dict):
            result.append(RapidSeenCancelOrderResponse(**res_data))
        return result

    async def get_account_balance(self) -> RapidSeenBalanceResponse:
        """استعلام موجودی حساب مدیریت در RapidSeen."""
        payload = {"action": "balance"}
        res_data = await self._post(payload)
        if isinstance(res_data, dict):
            return RapidSeenBalanceResponse(**res_data)
        raise RapidSeenAPIError("Unexpected response format for get_account_balance")