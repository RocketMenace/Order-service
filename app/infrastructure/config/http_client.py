from pydantic import Field
from pydantic_settings import BaseSettings


class HTTPClientSettings(BaseSettings):
    timeout_read: float = Field(
        default=30.0, description="Read timeout in seconds", gt=0
    )
    max_delay: int = Field(default=5, description="")
    max_retry: int = Field(default=5, description="")
