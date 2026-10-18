import aiohttp
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RapidSeenClient:
    def __init__(self, api_url: str = "https://rapidseen.com/api/v2", api_key: str = "dummy_key"):
        self.api_url = api_url
        self.api_key = api_key

    async def add_order(self, service_id: int, link: str, quantity: int) -> Dict[str, Any]:
        # Async client call placeholder for RapidSeen API
        logger.info(f"Sending order to RapidSeen: service={service_id}, link={link}, qty={quantity}")
        return {"status": "success", "order": 12345}