from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.modules.admissions.schemas import AdmissionRead


class DashboardSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    total_students: int = Field(default=0, serialization_alias="totalStudents")
    total_teachers: int = Field(default=0, serialization_alias="totalTeachers")
    total_staff: int = Field(default=0, serialization_alias="totalStaff")
    total_courses: int = Field(default=0, serialization_alias="totalCourses")
    total_subjects: int = Field(default=0, serialization_alias="totalSubjects")
    total_users: int = Field(default=0, serialization_alias="totalUsers")
    total_admissions: int = Field(default=0, serialization_alias="totalAdmissions")
    total_attendance_records: int = Field(default=0, serialization_alias="totalAttendanceRecords")
    total_marks_recorded: int = Field(default=0, serialization_alias="totalMarksRecorded")
    pending_fee_count: int = Field(default=0, serialization_alias="pendingFeeCount")
    pending_fee_amount: Decimal = Field(default=Decimal("0"), serialization_alias="pendingFeeAmount")
    recent_admissions: list[AdmissionRead] = Field(default_factory=list, serialization_alias="recentAdmissions")


class UserDashboard(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: str
    summary: dict[str, Any] | None = None
    profile: dict[str, Any] | None = None
    quick_stats: dict[str, Any] | None = Field(default=None, serialization_alias="quickStats")
    recent_attendance: list[dict[str, Any]] | None = Field(default=None, serialization_alias="recentAttendance")
    recent_fees: list[dict[str, Any]] | None = Field(default=None, serialization_alias="recentFees")
    pending_fees: list[dict[str, Any]] | None = Field(default=None, serialization_alias="pendingFees")
    recent_marks: list[dict[str, Any]] | None = Field(default=None, serialization_alias="recentMarks")
    courses: list[dict[str, Any]] | None = None
    subjects: list[dict[str, Any]] | None = None
    students_by_course: dict[str, int] | None = Field(default=None, serialization_alias="studentsByCourse")
    message: str | None = None

