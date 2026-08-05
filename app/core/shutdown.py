import asyncio
import logging
import signal
import sys
from typing import Callable, List

from app.core.logging import get_logger

logger = get_logger(__name__)

# لیستی از توابع پاکسازی که هنگام خاموش شدن باید اجرا شوند
_cleanup_callbacks: List[Callable] = []


def register_shutdown_callback(callback: Callable) -> None:
    """ثبت توابع پاکسازی (مانند بستن اتصالات دیتابیس یا ردیس)."""
    _cleanup_callbacks.append(callback)


async def graceful_shutdown(signal_name: str = "UNKNOWN") -> None:
    """اجرای ترتیبی تمام توابع پاکسازی ثبت‌شده هنگام دریافت سیگنال توقف."""
    logger.info("Received shutdown signal (%s). Starting graceful shutdown...", signal_name)
    
    for callback in _cleanup_callbacks:
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback()
            else:
                callback()
        except Exception as e:
            logger.error("Error executing cleanup callback %s: %s", callback.__name__, e)

    logger.info("Graceful shutdown completed successfully. Exiting process.")


def setup_signal_handlers(loop: asyncio.AbstractEventLoop) -> None:
    """تنظیم شنونده‌های سیگنال‌های SIGINT و SIGTERM در Event Loop."""
    if sys.platform != "win32":
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(
                    sig,
                    lambda s=sig: asyncio.create_task(graceful_shutdown(s.name))
                )
            except NotImplementedError:
                pass
    else:
        # در ویندوز اضافه کردن signal handler به event loop محدودیت دارد
        logger.debug("Windows environment detected. Signal handling managed via standard asyncio try-finally blocks.")