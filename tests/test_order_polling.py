import asyncio
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services import order_polling


async def test_one_polling_round_processes_open_orders():
    @asynccontextmanager
    async def maker():
        yield MagicMock()

    with patch.object(order_polling, "async_session_maker", maker), \
         patch.object(order_polling, "OrderLifecycleService") as lifecycle:
        lifecycle.return_value.process_open_orders = AsyncMock()
        client = MagicMock()
        await order_polling.poll_open_orders_once(client)
    lifecycle.return_value.process_open_orders.assert_awaited_once()
    assert lifecycle.call_args.args[1] is client


async def test_polling_loop_survives_a_failed_round():
    calls = {"n": 0}

    async def flaky(_client):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("provider down")

    sleeps = {"n": 0}

    async def fake_sleep(_seconds):
        sleeps["n"] += 1
        if sleeps["n"] >= 2:
            raise asyncio.CancelledError

    with patch.object(order_polling, "poll_open_orders_once", flaky), \
         patch.object(order_polling.asyncio, "sleep", fake_sleep):
        with pytest.raises(asyncio.CancelledError):
            await order_polling.poll_open_orders_forever(1)
    assert calls["n"] == 2
