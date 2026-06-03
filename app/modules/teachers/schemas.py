from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field


class TeacherWriteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    teacher_code: str | None = Field(default=None, validation_alias=AliasChoices("teacherCode", "teacher_code"))
    first_name: str | None = Field(default=None, validation_alias=AliasChoices("firstName", "first_name"))
    last_name: str | None = Field(default=None, validation_alias=AliasChoices("lastName", "last_name"))
    dob: date | None = None
    gender: str | None = None
    phone_number: str | None = Field(default=None, validation_alias=AliasChoices("phoneNumber", "phone_number"))
    email: EmailStr | None = None
    hire_date: date | None = Field(default=None, validation_alias=AliasChoices("hireDate", "hire_date"))
    department: str | None = None
    address: str | None = None
    qualification: str | None = None
    salary: Decimal | None = None
    course_codes: list[str] | None = Field(default=None, validation_alias=AliasChoices("courseCodes", "course_codes"))
    subject_ids: list[int] | None = Field(default=None, validation_alias=AliasChoices("subjectIds", "subject_ids"))


class TeacherRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    teacher_id: int | None = Field(default=None, serialization_alias="teacherId")
    teacher_code: str | None = Field(default=None, serialization_alias="teacherCode")
    first_name: str | None = Field(default=None, serialization_alias="firstName")
    last_name: str | None = Field(default=None, serialization_alias="lastName")
    dob: date | None = None
    gender: str | None = None
    phone_number: str | None = Field(default=None, serialization_alias="phoneNumber")
    email: str | None = None
    hire_date: date | None = Field(default=None, serialization_alias="hireDate")
    department: str | None = None
    address: str | None = None
    qualification: str | None = None
    salary: Decimal | None = None
    course_codes: list[str] = Field(default_factory=list, serialization_alias="courseCodes")
    subject_ids: list[int] = Field(default_factory=list, serialization_alias="subjectIds")
    created_at: datetime | None = Field(default=None, serialization_alias="createdAt")


class CourseAssignmentRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    course_codes: list[str] = Field(default_factory=list, validation_alias=AliasChoices("courseCodes", "course_codes"))


class SubjectAssignmentRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    subject_ids: list[int] = Field(default_factory=list, validation_alias=AliasChoices("subjectIds", "subject_ids"))

