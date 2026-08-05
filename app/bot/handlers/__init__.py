from aiogram import Router
from app.bot.handlers.start import router as start_router


def get_handlers_router() -> Router:
    """ترکیب تمام روترهای هندلرها در یک روتر اصلی."""
    router = Router()
    router.include_router(start_router)
    return router


__all__ = ["get_handlers_router"]