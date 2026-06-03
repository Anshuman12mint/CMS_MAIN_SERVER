from __future__ import annotations

from fastapi import HTTPException, status


GENDERS = {"Male", "Female", "Other"}
BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"}
ATTENDANCE_STATUSES = {"Present", "Absent"}
FEE_STATUSES = {"Paid", "Pending"}
USER_ROLES = {"Student", "Teacher", "Staff", "Admin"}
ACCOUNT_STATUSES = {"ACTIVE", "LOCKED", "DISABLED"}
EXAM_TYPES = {"Midterm", "Final", "Assignment", "Practical", "Other"}
STAFF_ROLES = {
    "Administration",
    "Librarian",
    "Clerk",
    "Lab Assistant",
    "Maintenance",
    "Security",
    "Other",
}


def has_text(value: str | None) -> bool:
    return value is not None and value.strip() != ""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def require_text(value: str | None, field_name: str) -> None:
    require(has_text(value), f"{field_name} is required")


def normalize_required_choice(value: str | None, allowed_values: set[str], field_name: str) -> str:
    require_text(value, field_name)
    return _normalize_choice(value, allowed_values, field_name)


def normalize_optional_choice(value: str | None, allowed_values: set[str], field_name: str) -> str | None:
    if not has_text(value):
        return None
    return _normalize_choice(value, allowed_values, field_name)


def _normalize_choice(value: str | None, allowed_values: set[str], field_name: str) -> str:
    assert value is not None
    trimmed = value.strip()
    for option in allowed_values:
        if option.lower() == trimmed.lower():
            return option
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"{field_name} must be one of: {', '.join(sorted(allowed_values))}",
    )
