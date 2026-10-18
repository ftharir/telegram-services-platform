class PlatformBaseException(Exception):
    """Base exception for platform"""
    pass

class InsufficientBalanceError(PlatformBaseException):
    """Raised when user balance is not enough"""
    pass