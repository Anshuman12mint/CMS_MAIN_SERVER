from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class StudentMarkWriteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    student_id: int | None = Field(default=None, validation_alias=AliasChoices("studentId", "student_id"))
    subject_id: int | None = Field(default=None, validation_alias=AliasChoices("subjectId", "subject_id"))
    semester: int | None = None
    exam_type: str | None = Field(default=None, validation_alias=AliasChoices("examType", "exam_type"))
    marks_obtained: Decimal | None = Field(default=None, validation_alias=AliasChoices("marksObtained", "marks_obtained"))
    max_marks: Decimal | None = Field(default=None, validation_alias=AliasChoices("maxMarks", "max_marks"))
    grade: str | None = None
    exam_date: date | None = Field(default=None, validation_alias=AliasChoices("examDate", "exam_date"))


class StudentMarkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    mark_id: int | None = Field(default=None, serialization_alias="markId")
    student_id: int | None = Field(default=None, serialization_alias="studentId")
    subject_id: int | None = Field(default=None, serialization_alias="subjectId")
    semester: int | None = None
    exam_type: str | None = Field(default=None, serialization_alias="examType")
    marks_obtained: Decimal | None = Field(default=None, serialization_alias="marksObtained")
    max_marks: Decimal | None = Field(default=None, serialization_alias="maxMarks")
    grade: str | None = None
    exam_date: date | None = Field(default=None, serialization_alias="examDate")

