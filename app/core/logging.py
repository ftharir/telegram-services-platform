import logging  
import sys  
from app.core.config import settings  


def setup_logging() -> None:
    """پیکربندی و راه‌اندازی سیستم لاگینگ پروژه."""
    
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    
    log_format = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
     
    
    date_format = "%Y-%m-%d %H:%M:%S"

    
    logging.basicConfig(
        level=log_level,  
        format=log_format,  
        datefmt=date_format,  
        handlers=[
            
            logging.StreamHandler(sys.stdout)
        ]
    )
 
    
    logging.getLogger("aiogram").setLevel(logging.INFO)  
    logging.getLogger("asyncio").setLevel(logging.WARNING)  
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)  

    
    logger = logging.getLogger(__name__)
    
    
    logger.info(f"Logging configured successfully. Environment: {settings.ENVIRONMENT}, Debug: {settings.DEBUG}")


def get_logger(name: str) -> logging.Logger:
    """دریافت یک Logger اختصاصی برای هر ماژول یا فایل.
    
    Args:
        name (str): معمولاً __name__ فایل ارسال می‌شود.
        
    Returns:
        logging.Logger: شیء لاگر آماده برای ثبت پیام.
    """
    
    return logging.getLogger(name)

