from .base import InfrastructureException


class HTTPClientException(InfrastructureException):
    def __init__(self):
        message = "Service temporarily unavailable"
        super().__init__(message)
