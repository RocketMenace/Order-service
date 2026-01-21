import asyncio
import random
from typing import Any, Self

import httpx
from fastapi import status

from ..config.http_client import HTTPClientSettings


class BaseHTTPXClient:
    RETRYABLE_STATUS_CODES = (
        status.HTTP_408_REQUEST_TIMEOUT,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        status.HTTP_503_SERVICE_UNAVAILABLE,
        status.HTTP_504_GATEWAY_TIMEOUT,
        status.HTTP_400_BAD_REQUEST,
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
        for attempt in range(self.config.max_retry + 1):
            try:
                response = await self._client.request(
                    method=method, url=url, params=params, headers=headers, json=json
                )
                if response.status_code in self.RETRYABLE_STATUS_CODES:
                    if attempt < self.config.max_retry:
                        delay = self._calculate_jitter_delay(attempt)
                        await asyncio.sleep(delay)
                        continue
                return response

            except self.RETRYABLE_EXCEPTIONS as e:
                last_exception = e
                if attempt < self.config.max_retry:
                    delay = self._calculate_jitter_delay(attempt)
                    await asyncio.sleep(delay)
                    continue

            except httpx.HTTPStatusError as e:
                if e.response.status_code not in self.RETRYABLE_STATUS_CODES:
                    raise
                last_exception = e
                if attempt < self.config.max_retry:
                    delay = self._calculate_jitter_delay(attempt)
                    await asyncio.sleep(delay)
                    continue
        if last_exception:
            raise last_exception
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
