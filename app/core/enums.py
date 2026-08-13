from enum import Enum


class TransactionType(str, Enum):
    """انواع تراکنش‌های مالی سیستم کیف پول."""
    CREDIT = "CREDIT"          # افزایش موجودی (واریز/هدیه)
    DEBIT = "DEBIT"            # کاهش موجودی (خرید/ثبت سفارش)
    REFUND = "REFUND"          # بازگشت وجه (لغو یا نقص سفارش)
    ADJUSTMENT = "ADJUSTMENT"  # اصلاحیه دستی توسط مدیریت