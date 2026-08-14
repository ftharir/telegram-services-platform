from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class RapidSeenAddOrderResponse(BaseModel):
    """پاسخ درخواست ثبت سفارش در RapidSeen API."""
    order: Optional[Union[int, str]] = None
    error: Optional[str] = None


class RapidSeenOrderStatusResponse(BaseModel):
    """پاسخ درخواست استعلام وضعیت سفارش."""
    charge: Optional[str] = None
    start_count: Optional[Union[int, str]] = Field(default=None, alias="start_count")
    status: Optional[str] = None
    remains: Optional[Union[int, str]] = None
    currency: Optional[str] = None
    error: Optional[str] = None


class RapidSeenCancelOrderResponse(BaseModel):
    """پاسخ درخواست لغو سفارش."""
    order: Optional[Union[int, str]] = None
    cancel: Optional[Union[int, str, bool]] = None
    error: Optional[str] = None


class RapidSeenBalanceResponse(BaseModel):
    """پاسخ استعلام موجودی اکانت مدیریت در RapidSeen."""
    balance: Optional[str] = None
    currency: Optional[str] = None
    error: Optional[str] = None