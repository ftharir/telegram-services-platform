from typing import Optional
from pydantic import BaseModel, Field

class RapidSeenAddOrderResponse(BaseModel):
    order: Optional[int] = None
    error: Optional[str] = None

class RapidSeenOrderStatusResponse(BaseModel):
    status: Optional[str] = None
    charge: Optional[str] = None
    start_count: Optional[str] = None
    remains: Optional[int] = None
    currency: Optional[str] = None
    error: Optional[str] = None

class RapidSeenCancelOrderResponse(BaseModel):
    cancel: Optional[str] = None  # Sent, Already sent, Not possible
    error: Optional[str] = None
