import asyncio
from app.database.session import async_session_maker
from app.services.wallet_service import WalletService, InsufficientBalanceError
from tests.conftest import make_user

async def test():
    async with async_session_maker() as session:
        user = await make_user(session)
        service = WalletService(session)
        w, tx1 = await service.credit(user.id, 100)
        print("Credited 100 coins. New balance:", w.balance)
        w, tx2 = await service.debit(user.id, 40)
        print("Debited 40 coins. New balance:", w.balance)
        try:
            await service.debit(user.id, 200)
        except InsufficientBalanceError:
            print("Insufficient balance test PASSED!")
        await session.rollback()

if __name__ == "__main__":
    asyncio.run(test())
