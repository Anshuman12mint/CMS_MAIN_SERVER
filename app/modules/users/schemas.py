from __future__ import annotations

from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: int | None = Field(default=None, serialization_alias="userId")
    login_id: str | None = Field(default=None, serialization_alias="loginId")
    username: str | None = None
    email: str | None = None
    role: str | None = None
    student_id: int | None = Field(default=None, serialization_alias="studentId")
    teacher_id: int | None = Field(default=None, serialization_alias="teacherId")
    staff_id: int | None = Field(default=None, serialization_alias="staffId")
    profile_type: str | None = Field(default=None, serialization_alias="profileType")
    profile_id: int | None = Field(default=None, serialization_alias="profileId")
    account_status: str | None = Field(default=None, serialization_alias="accountStatus")
    registered_at: datetime | None = Field(default=None, serialization_alias="registeredAt")
    last_login_at: datetime | None = Field(default=None, serialization_alias="lastLoginAt")
    created_at: datetime | None = Field(default=None, serialization_alias="createdAt")


class UserMutationRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    login_id: str | None = Field(default=None, validation_alias=AliasChoices("loginId", "login_id"))
    username: str | None = None
    password: str | None = Field(default=None, min_length=8, max_length=100)
    email: EmailStr | None = None
    role: str
    student_id: int | None = Field(default=None, validation_alias=AliasChoices("studentId", "student_id"))
    teacher_id: int | None = Field(default=None, validation_alias=AliasChoices("teacherId", "teacher_id"))
    staff_id: int | None = Field(default=None, validation_alias=AliasChoices("staffId", "staff_id"))
    account_status: str | None = Field(default=None, validation_alias=AliasChoices("accountStatus", "account_status"))

    @model_validator(mode="after")
    def normalize_legacy_username(self) -> UserMutationRequest:
        if self.login_id is None and self.username is not None:
            self.login_id = self.username
        return self

