from fastapi import APIRouter, status
from ..schemas.order import OrderResponseSchema, OrderRequestSchema
from ..schemas.payment import PaymentRequestSchema
from ..schemas.response import ApiResponseSchema
from dishka.integrations.fastapi import inject, FromDishka
from app.application.use_cases.create_order import CreateOrderUseCase
from app.application.use_cases.payments_response import HandlePaymentResponseUseCase


router = APIRouter(
    prefix="/orders",
    tags=[
        "v1 Orders",
    ],
)


@router.post(
    path="",
    summary="Create a new order",
    description="""
    Create a new order for a specific item.
    
    This endpoint allows users to create a new order by specifying the item they want to purchase, 
    the quantity, and providing an idempotency key to prevent duplicate orders.
    
    **Request Body Parameters:**
    - `item_id` (UUID, required): The unique UUID identifier of the item to order
    - `quantity` (integer, required): The quantity of items to order. Must be at least 1
    - `user_id` (string, required): The unique identifier of the user placing the order
    - `idempotency_key` (UUID, required): A unique key to ensure idempotency of the request
    
    **Response Body:**
    - `id`: Unique identifier for the created order
    - `item_id`: The item ID that was ordered
    - `quantity`: The quantity of items ordered
    - `status`: The current status of the order (e.g., "new")
    - `created_at`: Timestamp when the order was created
    - `updated_at`: Timestamp when the order was last updated
    
    **Process:**
    1. Validates that the item exists in the catalog
    2. Checks if sufficient stock is available
    3. Creates the order record
    4. Initiates payment processing
    5. Creates an outbox event for order creation
    """,
    response_model=ApiResponseSchema[OrderResponseSchema],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Order created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "id": "9a4f56ba-1979-4fd1-a16e-b0727c472173",
                            "item_id": "de71f1c7-674d-4569-ad05-5f1367ccc4ce",
                            "quantity": 2,
                            "status": "new",
                            "created_at": "2025-10-31T14:12:57.868385+00:00",
                            "updated_at": "2025-10-31T14:12:57.868385+00:00",
                        },
                        "meta": {
                            "path": "/api/v1/orders",
                            "method": "POST",
                        },
                        "errors": [],
                    },
                },
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Item not found",
            "content": {
                "application/json": {
                    "example": {
                        "data": {},
                        "meta": {
                            "path": "/api/v1/orders",
                            "method": "POST",
                        },
                        "errors": [
                            {
                                "message": "Item with de71f1c7-674d-4569-ad05-5f1367ccc4ce not found.",
                                "field": "item_id",
                                "detail": "Item ID: de71f1c7-674d-4569-ad05-5f1367ccc4ce",
                            },
                        ],
                    },
                },
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Insufficient stock available",
            "content": {
                "application/json": {
                    "example": {
                        "data": {},
                        "meta": {
                            "path": "/api/v1/orders",
                            "method": "POST",
                        },
                        "errors": [
                            {
                                "message": "Item is out of stock. Not enough quantity available.",
                                "detail": "The requested quantity exceeds available stock",
                            },
                        ],
                    },
                },
            },
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "data": {},
                        "meta": {
                            "path": "/api/v1/orders",
                            "method": "POST",
                        },
                        "errors": [
                            {
                                "field": "quantity",
                                "message": "ensure this value is greater than or equal to 1",
                                "input": 0,
                            },
                        ],
                    },
                },
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error - connection to external service failed",
            "content": {
                "application/json": {
                    "example": {
                        "data": {},
                        "meta": {
                            "path": "/api/v1/orders",
                            "method": "POST",
                        },
                        "errors": [
                            {
                                "message": "All connection attempts failed",
                                "detail": "Service temporarily unavailable",
                            },
                        ],
                    },
                },
            },
        },
    },
)
@inject
async def create_order(
    order: OrderRequestSchema,
    use_case: FromDishka["CreateOrderUseCase"],
):
    data = await use_case(order_dto=order.to_dto())
    return ApiResponseSchema(data=data, meta={}, errors=[])


@router.post(
    path="/payment-callback",
    summary="Process payment callback from Payments service",
    description="""
    Receive and process payment status callbacks from the Payments service.
    
    This endpoint is called by the Payments service to notify the Order service about 
    the status of a payment transaction. The endpoint handles payment status updates 
    and triggers appropriate actions based on whether the payment succeeded or failed.
    
    **Request Body Parameters:**
    - `id` (UUID, required): Unique identifier of the payment transaction
    - `user_id` (UUID, required): Unique identifier of the user who made the payment
    - `order_id` (UUID, required): Unique identifier of the order associated with the payment
    - `amount` (Decimal, required): The payment amount
    - `status` (PaymentStatusEnum, optional): Payment status - "pending", "succeeded", or "failed". Defaults to "pending"
    - `idempotency_key` (UUID, required): Unique key to ensure idempotency and prevent duplicate processing
    - `created_at` (datetime, required): Timestamp when the payment was created
    
    **Payment Status Handling:**
    - **SUCCEEDED**: Creates an ORDER_PAID inbox event and a notification for successful payment
    - **FAILED**: Creates an ORDER_CANCELLED inbox event and a notification for failed payment
    - **PENDING**: No action taken (payment still in progress)
    
    **Idempotency:**
    - The endpoint checks if a payment with the same `idempotency_key` has already been processed
    - If already processed, returns success without creating duplicate events
    - This ensures the endpoint is safe to retry
    
    **Response:**
    - Returns HTTP 200 OK with empty data payload on successful processing
    - The actual processing happens asynchronously via inbox events
    """,
    # response_model=ApiResponseSchema[dict],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "Payment callback processed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": {},
                        "meta": {
                            "path": "/api/v1/orders/payment-callback",
                            "method": "POST",
                        },
                        "errors": [],
                    },
                },
            },
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Validation error - invalid request body",
            "content": {
                "application/json": {
                    "example": {
                        "data": {},
                        "meta": {
                            "path": "/api/v1/orders/payment-callback",
                            "method": "POST",
                        },
                        "errors": [
                            {
                                "field": "order_id",
                                "message": "field required",
                                "input": {},
                            },
                        ],
                    },
                },
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad request - invalid payment data",
            "content": {
                "application/json": {
                    "example": {
                        "data": {},
                        "meta": {
                            "path": "/api/v1/orders/payment-callback",
                            "method": "POST",
                        },
                        "errors": [
                            {
                                "message": "Invalid payment status",
                                "detail": "Payment status must be one of: pending, succeeded, failed",
                            },
                        ],
                    },
                },
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error - failed to process payment callback",
            "content": {
                "application/json": {
                    "example": {
                        "data": {},
                        "meta": {
                            "path": "/api/v1/orders/payment-callback",
                            "method": "POST",
                        },
                        "errors": [
                            {
                                "message": "Failed to process payment callback",
                                "detail": "Database connection error",
                            },
                        ],
                    },
                },
            },
        },
    },
)
@inject
async def payment_callback(
    payment: PaymentRequestSchema, use_case: FromDishka["HandlePaymentResponseUseCase"]
):
    await use_case(payment=payment.to_dto())
    return ApiResponseSchema(data={}, meta={}, errors=[])
