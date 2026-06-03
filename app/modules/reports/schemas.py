from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.attendance.schemas import AttendanceRead
from app.modules.courses.schemas import CourseRead
from app.modules.fees.schemas import FeeRead
from app.modules.marks.schemas import StudentMarkRead
from app.modules.students.schemas import StudentRead
from app.modules.subjects.schemas import SubjectRead
from app.modules.teachers.schemas import TeacherRead


class StudentReport(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    student: StudentRead | None = None
    present_days: int = Field(default=0, serialization_alias="presentDays")
    absent_days: int = Field(default=0, serialization_alias="absentDays")
    total_fees: Decimal = Field(default=Decimal("0"), serialization_alias="totalFees")
    paid_fees: Decimal = Field(default=Decimal("0"), serialization_alias="paidFees")
    pending_fees_amount: Decimal = Field(default=Decimal("0"), serialization_alias="pendingFeesAmount")
    attendance: list[AttendanceRead] = Field(default_factory=list)
    fees: list[FeeRead] = Field(default_factory=list)
    marks: list[StudentMarkRead] = Field(default_factory=list)


class TeacherReport(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    teacher: TeacherRead | None = None
    courses: list[CourseRead] = Field(default_factory=list)
    subjects: list[SubjectRead] = Field(default_factory=list)


class FeeSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    paid_count: int = Field(default=0, serialization_alias="paidCount")
    pending_count: int = Field(default=0, serialization_alias="pendingCount")
    paid_amount: Decimal = Field(default=Decimal("0"), serialization_alias="paidAmount")
    pending_amount: Decimal = Field(default=Decimal("0"), serialization_alias="pendingAmount")
    pending_fees: list[FeeRead] = Field(default_factory=list, serialization_alias="pendingFees")

