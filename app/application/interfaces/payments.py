from typing import Protocol
from .contracts import PaymentRequest


class PaymentServiceProtocol(Protocol):
    async def create_payment(self, payload: PaymentRequest) -> bool: ...
