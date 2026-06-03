from __future__ import annotations

from datetime import date, datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field


class StudentWriteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    student_code: str | None = Field(default=None, validation_alias=AliasChoices("studentCode", "student_code"))
    first_name: str | None = Field(default=None, validation_alias=AliasChoices("firstName", "first_name"))
    last_name: str | None = Field(default=None, validation_alias=AliasChoices("lastName", "last_name"))
    dob: date | None = None
    gender: str | None = None
    phone_number: str | None = Field(default=None, validation_alias=AliasChoices("phoneNumber", "phone_number"))
    email: EmailStr | None = None
    course_code: str | None = Field(default=None, validation_alias=AliasChoices("courseCode", "course_code"))
    admission_date: date | None = Field(default=None, validation_alias=AliasChoices("admissionDate", "admission_date"))
    address: str | None = None
    guardian_name: str | None = Field(default=None, validation_alias=AliasChoices("guardianName", "guardian_name"))
    guardian_contact: str | None = Field(default=None, validation_alias=AliasChoices("guardianContact", "guardian_contact"))
    blood_group: str | None = Field(default=None, validation_alias=AliasChoices("bloodGroup", "blood_group"))


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    student_id: int | None = Field(default=None, serialization_alias="studentId")
    student_code: str | None = Field(default=None, serialization_alias="studentCode")
    first_name: str | None = Field(default=None, serialization_alias="firstName")
    last_name: str | None = Field(default=None, serialization_alias="lastName")
    dob: date | None = None
    gender: str | None = None
    phone_number: str | None = Field(default=None, serialization_alias="phoneNumber")
    email: str | None = None
    course_code: str | None = Field(default=None, serialization_alias="courseCode")
    admission_date: date | None = Field(default=None, serialization_alias="admissionDate")
    address: str | None = None
    guardian_name: str | None = Field(default=None, serialization_alias="guardianName")
    guardian_contact: str | None = Field(default=None, serialization_alias="guardianContact")
    blood_group: str | None = Field(default=None, serialization_alias="bloodGroup")
    created_at: datetime | None = Field(default=None, serialization_alias="createdAt")

