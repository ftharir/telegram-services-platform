import asyncio
from app.database.session import async_session_maker
from app.services.wallet_service import WalletService, InsufficientBalanceError

async def test():
    async with async_session_maker() as session:
        service = WalletService(session)
        w, tx1 = await service.credit(1, 100)
        print("Credited 100 coins. New balance:", w.balance)
        w, tx2 = await service.debit(1, 40)
        print("Debited 40 coins. New balance:", w.balance)
        try:
            await service.debit(1, 200)
        except InsufficientBalanceError:
            print("Insufficient balance test PASSED!")
        await session.rollback()

if __name__ == "__main__":
    asyncio.run(test())
