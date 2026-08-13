from typing import Dict, Optional, Union
from pydantic import BaseModel, Field


class RapidSeenAddOrderRequest(BaseModel):
    """مدل درخواست ثبت سفارش جدید به API."""
    key: str
    action: str = "add"
    service: int
    link: str
    quantity: int


class RapidSeenAddOrderResponse(BaseModel):
    """مدل پاسخ ثبت سفارش از API."""
    order: Optional[Union[int, str]] = None
    error: Optional[str] = None


class RapidSeenOrderStatusResponse(BaseModel):
    """مدل پاسخ استعلام وضعیت یک سفارش."""
    charge: Optional[str] = None
    start_count: Optional[Union[int, str]] = Field(default=None, alias="start_count")
    status: Optional[str] = None
    remains: Optional[Union[int, str]] = None
    currency: Optional[str] = None
    error: Optional[str] = None


class RapidSeenBalanceResponse(BaseModel):
    """مدل پاسخ دریافت موجودی حساب API."""
    balance: Optional[str] = None
    currency: Optional[str] = None
    error: Optional[str] = None