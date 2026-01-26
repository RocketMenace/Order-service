from typing import Any, Generic, Sequence, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ApiResponseSchema(BaseModel, Generic[DataT]):
    data: DataT | dict = Field(
        default_factory=dict,
        description="Response data payload.",
    )
    meta: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about the response",
    )
    errors: Sequence[Any] = Field(
        default_factory=list,
        description="List of errors, empty if successful",
    )
