from __future__ import annotations

from datetime import date, datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field, model_validator


class LoginRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    login_id: str | None = Field(default=None, validation_alias=AliasChoices("loginId", "login_id"))
    username: str | None = None
    password: str

    @model_validator(mode="after")
    def normalize_legacy_username(self) -> LoginRequest:
        if self.login_id is None and self.username is not None:
            self.login_id = self.username
        return self


class RefreshRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    refresh_token: str = Field(validation_alias=AliasChoices("refreshToken", "refresh_token"))


class StudentRegistrationRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    student_id: int | None = Field(default=None, validation_alias=AliasChoices("studentId", "student_id"))
    student_code: str | None = Field(default=None, validation_alias=AliasChoices("studentCode", "student_code"))
    login_id: str | None = Field(default=None, validation_alias=AliasChoices("loginId", "login_id"))
    username: str | None = None
    email: EmailStr
    dob: date
    password: str = Field(min_length=8, max_length=100)

    @model_validator(mode="after")
    def normalize_registration(self) -> StudentRegistrationRequest:
        if self.login_id is None and self.username is not None:
            self.login_id = self.username
        if self.student_id is None and self.student_code is None:
            raise ValueError("studentId or studentCode is required")
        return self


class LogoutRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    refresh_token: str = Field(validation_alias=AliasChoices("refreshToken", "refresh_token"))


class AuthResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    token: str
    access_token: str = Field(serialization_alias="accessToken")
    refresh_token: str = Field(serialization_alias="refreshToken")
    token_type: str = Field(default="Bearer", serialization_alias="tokenType")
    issued_at: datetime = Field(serialization_alias="issuedAt")
    expires_at: datetime = Field(serialization_alias="expiresAt")
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
