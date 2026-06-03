from __future__ import annotations

import re
from typing import Iterable, TypeVar


T = TypeVar("T")


def full_name(first_name: str | None, last_name: str | None) -> str:
    return " ".join(part.strip() for part in (first_name, last_name) if part and part.strip())


def trim_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed or None


def normalize_code(value: str | None) -> str | None:
    trimmed = trim_to_none(value)
    if trimmed is None:
        return None
    return re.sub(r"\s+", "", trimmed).upper()


def distinct_list(values: Iterable[T] | None) -> list[T]:
    if values is None:
        return []
    seen: list[T] = []
    for value in values:
        if value is None or value in seen:
            continue
        seen.append(value)
    return seen

