from __future__ import annotations

from math import ceil
from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


class PageResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)

    items: list[T]
    page: int
    page_size: int = Field(serialization_alias="pageSize")
    total_items: int = Field(serialization_alias="totalItems")
    total_pages: int = Field(serialization_alias="totalPages")


class PageQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=100)


def paginate_items(items: Sequence[T], page: int, page_size: int) -> PageResponse[T]:
    total_items = len(items)
    total_pages = max(1, ceil(total_items / page_size)) if page_size > 0 else 1
    start = (page - 1) * page_size
    end = start + page_size
    return PageResponse[T](
        items=list(items[start:end]),
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
    )
