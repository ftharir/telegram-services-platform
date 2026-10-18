from unittest.mock import AsyncMock, MagicMock, patch

from app.integrations.rapidseen.client import RapidSeenClient, RapidSeenAPIError


def _response(payload):
    resp = MagicMock()
    resp.json.return_value = payload
    return resp


async def test_add_order_returns_order_id():
    client = RapidSeenClient(api_key="test_key_123")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as post:
        post.return_value = _response({"order": 884422})
        res = await client.add_order(service_id=10, link="https://t.me/test/1", quantity=100)
    assert res.order == 884422 and res.error is None
    sent = post.call_args.kwargs["data"]
    assert sent["action"] == "add" and sent["service"] == 10 and sent["quantity"] == 100


async def test_get_status_maps_fields():
    client = RapidSeenClient(api_key="test_key_123")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as post:
        post.return_value = _response({"status": "Partial", "remains": 25, "charge": "0.5"})
        res = await client.get_status(884422)
    assert res.status == "Partial" and res.remains == 25


async def test_cancel_order_returns_cancel_result():
    client = RapidSeenClient(api_key="test_key_123")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as post:
        post.return_value = _response({"cancel": "Sent"})
        res = await client.cancel_order(884422)
    assert res.cancel == "Sent"


async def test_network_error_is_returned_as_error_field():
    client = RapidSeenClient(api_key="test_key_123")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as post:
        post.side_effect = RuntimeError("timeout")
        res = await client.add_order(service_id=1, link="https://t.me/test/1", quantity=100)
    assert res.order is None and "timeout" in res.error


def test_api_error_class_is_an_exception():
    assert issubclass(RapidSeenAPIError, Exception)
