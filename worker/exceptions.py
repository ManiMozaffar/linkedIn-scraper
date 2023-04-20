class BaseException(Exception):
    """Base Exception Class"""


class NoProxyException(BaseException):
    """Raised when there is Proxy initilized"""


class NoJobException(BaseException):
    """Raised when there is Job initilized"""


class NoJsonFound(BaseException):
    """Raised when there is no Json found in ChatGPT's answer"""
