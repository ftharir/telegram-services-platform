from aiogram import Router
from .start import router as start_router
from .account import router as account_router
from .view_handler import router as view_router
from .view_multiple_handler import router as view_multiple_router
from .order_tracking_handler import router as tracking_router


def get_handlers_router() -> Router:
    router = Router()
    router.include_router(view_router)
    router.include_router(view_multiple_router)
    router.include_router(tracking_router)
    router.include_router(account_router)
    router.include_router(start_router)
    return router
