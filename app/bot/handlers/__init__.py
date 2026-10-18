from aiogram import Router
from .start import router as start_router
from .account import router as account_router

def get_handlers_router() -> Router:
    router = Router()
    router.include_router(account_router)
    router.include_router(start_router)
    return router
