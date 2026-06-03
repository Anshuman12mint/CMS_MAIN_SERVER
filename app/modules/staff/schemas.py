from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field


class StaffWriteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    staff_code: str | None = Field(default=None, validation_alias=AliasChoices("staffCode", "staff_code"))
    first_name: str | None = Field(default=None, validation_alias=AliasChoices("firstName", "first_name"))
    last_name: str | None = Field(default=None, validation_alias=AliasChoices("lastName", "last_name"))
    dob: date | None = None
    gender: str | None = None
    phone_number: str | None = Field(default=None, validation_alias=AliasChoices("phoneNumber", "phone_number"))
    email: EmailStr | None = None
    hire_date: date | None = Field(default=None, validation_alias=AliasChoices("hireDate", "hire_date"))
    role: str | None = None
    department: str | None = None
    address: str | None = None
    salary: Decimal | None = None


class StaffRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    staff_id: int | None = Field(default=None, serialization_alias="staffId")
    staff_code: str | None = Field(default=None, serialization_alias="staffCode")
    first_name: str | None = Field(default=None, serialization_alias="firstName")
    last_name: str | None = Field(default=None, serialization_alias="lastName")
    dob: date | None = None
    gender: str | None = None
    phone_number: str | None = Field(default=None, serialization_alias="phoneNumber")
    email: str | None = None
    hire_date: date | None = Field(default=None, serialization_alias="hireDate")
    role: str | None = None
    department: str | None = None
    address: str | None = None
    salary: Decimal | None = None
    created_at: datetime | None = Field(default=None, serialization_alias="createdAt")

