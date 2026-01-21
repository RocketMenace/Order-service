from typing import TypeVar

from app.infrastructure.models.base import BaseModel

TEntity = TypeVar("TEntity")

TModel = TypeVar("TModel", bound=BaseModel)
