from enum import Enum


class TransactionType(str, Enum):
    """انواع تراکنش‌های مالی سیستم کیف پول."""
    CREDIT = "CREDIT"          # افزایش موجودی (واریز/هدیه)
    DEBIT = "DEBIT"            # کاهش موجودی (خرید/ثبت سفارش)
    REFUND = "REFUND"          # بازگشت وجه (لغو یا نقص سفارش)
    ADJUSTMENT = "ADJUSTMENT"  # اصلاحیه دستی توسط مدیریت


class OrderStatus(str, Enum):
    """وضعیت‌های مختلف یک سفارش در سیستم داخلی."""
    PENDING = "PENDING"            # در انتظار پردازش و ارسال به API
    SUBMITTED = "SUBMITTED"        # ارسال‌شده به API و دریافت Order ID
    IN_PROGRESS = "IN_PROGRESS"    # در حال انجام توسط API
    COMPLETED = "COMPLETED"        # تکمیل‌شده به‌صورت کامل
    PARTIAL = "PARTIAL"            # تکمیل‌نشده / بخشی اجراشده
    CANCELED = "CANCELED"          # لغوشده
    FAILED = "FAILED"              # با خطا مواجه‌شده