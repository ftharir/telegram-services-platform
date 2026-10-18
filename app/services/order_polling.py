import asyncio

from app.core.config import settings
from app.core.logging import get_logger
from app.database.session import async_session_maker
from app.integrations.rapidseen.client import RapidSeenClient
from app.services.order_lifecycle_service import OrderLifecycleService

logger = get_logger(__name__)


async def poll_open_orders_once(client: RapidSeenClient) -> None:
    """یک دور بررسی وضعیت سفارش‌های باز در RapidSeen."""
    async with async_session_maker() as session:
        await OrderLifecycleService(session, client).process_open_orders()


async def poll_open_orders_forever(interval_seconds: int) -> None:
    """بررسی دوره‌ای سفارش‌های باز؛ خطای یک دور کل حلقه را متوقف نمی‌کند."""
    client = RapidSeenClient(api_key=settings.RAPIDSEEN_API_KEY, base_url=settings.RAPIDSEEN_API_URL)
    logger.info("Order status polling started (every %s s).", interval_seconds)
    while True:
        try:
            await poll_open_orders_once(client)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Order status polling failed; will retry.")
        await asyncio.sleep(interval_seconds)
