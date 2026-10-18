from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.bot.handlers import view_handler, view_multiple_handler
from app.services.order_placement_service import OrderPlacementError
from app.services.wallet_service import InsufficientBalanceError


def _session():
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    @asynccontextmanager
    async def maker():
        yield session

    return session, maker


def _callback():
    cb = MagicMock()
    cb.message.edit_text = AsyncMock()
    return cb


def _state(data):
    st = MagicMock()
    st.get_data = AsyncMock(return_value=data)
    st.clear = AsyncMock()
    return st


USER = SimpleNamespace(id=7)
SINGLE = {"quantity": 500, "target_link": "https://t.me/ch/1", "idempotency_key": "k1"}


async def _confirm_single(place_order):
    session, maker = _session()
    cb, st = _callback(), _state(SINGLE)
    with patch.object(view_handler, "async_session_maker", maker), \
         patch.object(view_handler, "OrderPlacementService") as svc:
        svc.return_value.place_order = place_order
        await view_handler.confirm_single_view(cb, st, USER)
    return session, cb, st


async def test_single_order_success_commits_and_shows_tracking_code():
    place = AsyncMock(return_value=SimpleNamespace(tracking_code="ORD-20260101-ABCDE"))
    session, cb, st = await _confirm_single(place)
    kwargs = place.call_args.kwargs
    assert kwargs["user_id"] == 7 and kwargs["cost_coins"] == 5 and kwargs["idempotency_key"] == "k1"
    session.commit.assert_awaited_once()
    assert "ORD-20260101-ABCDE" in cb.message.edit_text.call_args.args[0]
    st.clear.assert_awaited_once()


async def test_single_order_insufficient_balance_rolls_back():
    session, cb, st = await _confirm_single(AsyncMock(side_effect=InsufficientBalanceError("no")))
    session.rollback.assert_awaited_once()
    session.commit.assert_not_awaited()
    assert "کافی نیست" in cb.message.edit_text.call_args.args[0]


async def test_single_order_provider_failure_keeps_the_refund():
    session, cb, st = await _confirm_single(AsyncMock(side_effect=OrderPlacementError("api")))
    session.commit.assert_awaited_once()          # refund + FAILED status are saved
    assert "بازگردانده" in cb.message.edit_text.call_args.args[0]


async def test_multi_order_places_every_link_with_its_own_key():
    session, maker = _session()
    cb = _callback()
    st = _state({"quantity": 200, "valid_links": ["https://t.me/a_channel/1", "https://t.me/a_channel/2"], "batch_key": "b"})
    place = AsyncMock(side_effect=[SimpleNamespace(tracking_code="ORD-1"), SimpleNamespace(tracking_code="ORD-2")])
    with patch.object(view_multiple_handler, "async_session_maker", maker), \
         patch.object(view_multiple_handler, "OrderPlacementService") as svc:
        svc.return_value.place_order = place
        await view_multiple_handler.confirm_multi_view(cb, st, USER)
    keys = [c.kwargs["idempotency_key"] for c in place.call_args_list]
    assert keys == ["b-0", "b-1"]
    assert session.commit.await_count == 2
    text = cb.message.edit_text.call_args.args[0]
    assert "ORD-1" in text and "ORD-2" in text


async def test_multi_order_stops_when_balance_runs_out():
    session, maker = _session()
    cb = _callback()
    st = _state({"quantity": 200, "valid_links": ["https://t.me/a_channel/1", "https://t.me/a_channel/2"], "batch_key": "b"})
    place = AsyncMock(side_effect=[SimpleNamespace(tracking_code="ORD-1"), InsufficientBalanceError("no")])
    with patch.object(view_multiple_handler, "async_session_maker", maker), \
         patch.object(view_multiple_handler, "OrderPlacementService") as svc:
        svc.return_value.place_order = place
        await view_multiple_handler.confirm_multi_view(cb, st, USER)
    text = cb.message.edit_text.call_args.args[0]
    assert "ORD-1" in text and "1 لینک ثبت نشد" in text
