import asyncio
import random
from typing import Any, Self

import httpx
from fastapi import status

from app.infrastructure.config.http_client import HTTPClientSettings
from app.infrastructure.config.logging import get_logger

logger = get_logger(__name__)


class BaseHTTPXClient:
    RETRYABLE_STATUS_CODES = (
        status.HTTP_408_REQUEST_TIMEOUT,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        status.HTTP_503_SERVICE_UNAVAILABLE,
        status.HTTP_504_GATEWAY_TIMEOUT,
    )

    RETRYABLE_EXCEPTIONS = (
        httpx.TimeoutException,
        httpx.NetworkError,
        httpx.ConnectError,
        httpx.ReadTimeout,
    )

    def __init__(self, config: HTTPClientSettings):
        self.config = config
        self._client: httpx.AsyncClient | None = None
        self._base_delay = 1.0

    async def __aenter__(self) -> Self:
        timeout = httpx.Timeout(
            read=self.config.timeout_read,
            connect=5.0,
            write=5.0,
            pool=5.0,
        )
        self._client = httpx.AsyncClient(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _calculate_jitter_delay(self, attempt: int) -> float:
        exponential_delay = self._base_delay * (2**attempt)
        max_delay_seconds = float(self.config.max_delay)
        capped_delay = min(max_delay_seconds, exponential_delay)
        jittered_delay = random.uniform(0, capped_delay)
        return jittered_delay

    async def make_request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        last_exception = None
        total_attempts = self.config.max_retry + 1

        logger.info(
            "HTTP request initiated",
            method=method,
            url=url,
        )

        for attempt in range(total_attempts):
            try:
                response = await self._client.request(
                    method=method, url=url, params=params, headers=headers, json=json
                )
                logger.info(
                    "Response data: ",
                    status_code=response.status_code,
                    content=response.content,
                )
                if response.status_code in self.RETRYABLE_STATUS_CODES:
                    if attempt < self.config.max_retry:
                        delay = self._calculate_jitter_delay(attempt)
                        logger.warning(
                            "HTTP request received retryable status code, retrying",
                            method=method,
                            url=url,
                            status_code=response.status_code,
                        )
                        await asyncio.sleep(delay)
                        continue
                return response

            except self.RETRYABLE_EXCEPTIONS as e:
                last_exception = e
                exception_type = type(e).__name__

                if attempt < self.config.max_retry:
                    delay = self._calculate_jitter_delay(attempt)
                    logger.warning(
                        "HTTP request failed with retryable exception, retrying",
                        method=method,
                        url=url,
                        exception_type=exception_type,
                        exception_message=str(e),
                    )
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error(
                        "HTTP request failed with retryable exception, all retries exhausted",
                        method=method,
                        url=url,
                        exception_type=exception_type,
                    )

            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code if e.response else None

                if status_code not in self.RETRYABLE_STATUS_CODES:
                    logger.error(
                        "HTTP request failed with non-retryable status code",
                        method=method,
                        url=url,
                        status_code=status_code,
                    )
                    raise

                last_exception = e
                if attempt < self.config.max_retry:
                    delay = self._calculate_jitter_delay(attempt)
                    logger.warning(
                        "HTTP request failed with retryable HTTP status error, retrying",
                        method=method,
                        url=url,
                        status_code=status_code,
                    )
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error(
                        "HTTP request failed with retryable HTTP status error, all retries exhausted",
                        method=method,
                        url=url,
                        status_code=status_code,
                    )

        if last_exception:
            logger.error(
                "HTTP request failed after all retry attempts",
                method=method,
                url=url,
            )
            raise last_exception

        logger.error(
            "HTTP request failed after all retry attempts with unknown error",
            method=method,
            url=url,
            total_attempts=total_attempts,
        )
        raise httpx.RequestError("Request failed after all retry attempts")

    async def post(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        return await self.make_request(
            method="POST", url=url, params=params, headers=headers, json=json
        )

    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> httpx.Response:
        return await self.make_request(
            method="GET", url=url, params=params, headers=headers
        )
