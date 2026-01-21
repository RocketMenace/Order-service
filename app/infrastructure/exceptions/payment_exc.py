from .base import InfrastructureException


class PaymentServiceUnavailableException(InfrastructureException):
    def __init__(self):
        message = "Payment service is temporarily unavailable. Please try again later."
        super().__init__(message)
