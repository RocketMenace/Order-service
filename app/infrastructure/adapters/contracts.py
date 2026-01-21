from typing import TypedDict


class PaymentRequest(TypedDict):
    order_id: str
    amount: str
    callback_url: str | None
    idempotency_key: str


class NotificationRequest(TypedDict):
    message: str
    idempotency_key: str
