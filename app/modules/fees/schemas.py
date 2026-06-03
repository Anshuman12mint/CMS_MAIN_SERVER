from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class FeeWriteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    student_id: int | None = Field(default=None, validation_alias=AliasChoices("studentId", "student_id"))
    amount: Decimal | None = None
    status: str | None = None
    due_date: date | None = Field(default=None, validation_alias=AliasChoices("dueDate", "due_date"))


class FeeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    fee_id: int | None = Field(default=None, serialization_alias="feeId")
    student_id: int | None = Field(default=None, serialization_alias="studentId")
    amount: Decimal | None = None
    status: str | None = None
    due_date: date | None = Field(default=None, serialization_alias="dueDate")

