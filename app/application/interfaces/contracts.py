from typing import TypedDict


class PaymentRequest(TypedDict):
    order_id: str
    amount: str
    idempotency_key: str


class NotificationRequest(TypedDict):
    message: str
    idempotency_key: str


class BrokerMessageResponse(TypedDict):
    event_type: str
    order_id: str
    item_id: str
    quantity: int
    shipment_id: str


class BrokerMessageRequest(TypedDict):
    event_type: str
    order_id: str
    item_id: str
    quantity: str
    idempotency_key: str
