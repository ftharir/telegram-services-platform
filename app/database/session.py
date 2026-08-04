from typing import AsyncGenerator  
from sqlalchemy.ext.asyncio import (  
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import settings  
from app.core.logging import get_logger  


logger = get_logger(__name__)



engine = create_async_engine(
    url=settings.database_url,  
    echo=False,  
    future=True,  
    pool_pre_ping=True,  
    pool_size=10,  
    max_overflow=20,  
)


async_session_maker = async_sessionmaker(
    bind=engine,  
    class_=AsyncSession,  
    expire_on_commit=False,  
    autoflush=False,  
)



async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """تولید یک AsyncSession دیتابیس و بستن خودکار آن پس از اتمام کار.
    
    Yields:
        AsyncSession: جلسه فعال دیتابیس جهت اجرای کوئری‌ها.
    """
    async with async_session_maker() as session:
        try:
            yield session  
        except Exception as e:
            await session.rollback()  
            logger.error(f"Database session error: {e}")
            raise e
        finally:
            await session.close()  

            