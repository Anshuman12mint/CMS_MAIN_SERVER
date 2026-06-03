from __future__ import annotations

from datetime import date as date_type

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class AttendanceWriteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    student_id: int | None = Field(default=None, validation_alias=AliasChoices("studentId", "student_id"))
    date: date_type | None = None
    status: str | None = None


class AttendanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    attendance_id: int | None = Field(default=None, serialization_alias="attendanceId")
    student_id: int | None = Field(default=None, serialization_alias="studentId")
    date: date_type | None = None
    status: str | None = None
