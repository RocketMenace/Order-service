from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions.order import (
    ItemNotFoundError,
    NotEnoughStocksError,
    OrderAlreadyExistsError,
)
from app.infrastructure.exceptions.cache_exc import CacheClientException
from app.infrastructure.exceptions.payment_exc import PaymentServiceUnavailableException
from app.presentation.api.v1.schemas.response import ApiResponseSchema


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = []
        for error in exc.errors():
            error_dict = {
                "message": error.get("msg", "Validation error"),
            }
            if "loc" in error and len(error["loc"]) > 1:
                field_path = ".".join(str(loc) for loc in error["loc"][1:])
                error_dict["field"] = field_path
            if "input" in error:
                error_dict["input"] = error["input"]
            errors.append(error_dict)

        response_data = ApiResponseSchema(
            data={},
            meta={
                "path": str(request.url.path),
                "method": request.method,
            },
            errors=errors,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=response_data.model_dump(),
        )

    @app.exception_handler(ItemNotFoundError)
    async def item_not_found_handler(
        request: Request, exc: ItemNotFoundError
    ) -> JSONResponse:
        response_data = ApiResponseSchema(
            data={},
            meta={
                "path": str(request.url.path),
                "method": request.method,
            },
            errors=[
                {
                    "message": str(exc),
                    "field": "item_id",
                    "detail": f"Item ID: {exc.item_id}",
                }
            ],
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response_data.model_dump(),
        )

    @app.exception_handler(NotEnoughStocksError)
    async def not_enough_stocks_handler(
        request: Request, exc: NotEnoughStocksError
    ) -> JSONResponse:
        response_data = ApiResponseSchema(
            data={},
            meta={
                "path": str(request.url.path),
                "method": request.method,
            },
            errors=[
                {
                    "message": str(exc),
                    "detail": "The requested quantity exceeds available stock",
                }
            ],
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=response_data.model_dump(),
        )

    @app.exception_handler(OrderAlreadyExistsError)
    async def order_already_exists_handler(
        request: Request, exc: OrderAlreadyExistsError
    ) -> JSONResponse:
        response_data = ApiResponseSchema(
            data={},
            meta={
                "path": str(request.url.path),
                "method": request.method,
            },
            errors=[
                {
                    "message": str(exc),
                    "detail": "This order already in process",
                }
            ],
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=response_data.model_dump()
        )

    @app.exception_handler(CacheClientException)
    async def cache_client_exception_handler(
        request: Request, exc: CacheClientException
    ) -> JSONResponse:
        response_data = ApiResponseSchema(
            data={},
            meta={
                "path": str(request.url.path),
                "method": request.method,
            },
            errors=[
                {
                    "message": str(exc),
                    "detail": "Service is temporarily unavailable. Please try again later.",
                }
            ],
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_data.model_dump(),
        )

    @app.exception_handler(PaymentServiceUnavailableException)
    async def payment_service_unavailable_handler(
        request: Request, exc: PaymentServiceUnavailableException
    ) -> JSONResponse:
        response_data = ApiResponseSchema(
            data={},
            meta={
                "path": str(request.url.path),
                "method": request.method,
            },
            errors=[
                {
                    "message": str(exc),
                    "detail": "Payment service is temporarily unavailable. Please try again later.",
                }
            ],
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=response_data.model_dump(),
        )
