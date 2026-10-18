import secrets

import pytest_asyncio

from app.database.models.user import User
from app.database.session import engine


@pytest_asyncio.fixture(autouse=True)
async def _dispose_engine_after_test():
    # every test runs in its own event loop; drop pooled connections so the next test opens fresh ones
    yield
    await engine.dispose()


async def make_user(session) -> User:
    """Create a throw-away user inside the test's transaction (the tests roll back at the end)."""
    user = User(telegram_id=secrets.randbelow(10**9) + 10**9, first_name="TestUser")
    session.add(user)
    await session.flush()
    return user
