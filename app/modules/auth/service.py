from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta

from fastapi import HTTPException, status

from app.common import helpers, validators
from app.core.config import get_settings, utc_now
from app.core.security import hash_password, verify_password
from app.modules.auth.jwt import JwtService
from app.modules.auth.models import RefreshToken
from app.modules.auth.refresh_token_repository import RefreshTokenRepository
from app.modules.auth.schemas import AuthResponse, LoginRequest, LogoutRequest, RefreshRequest, StudentRegistrationRequest
from app.modules.students.model import Student
from app.modules.students.repository import StudentRepository
from app.modules.users.model import User
from app.modules.users.repository import UserRepository


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        jwt_service: JwtService,
    ) -> None:
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository
        self.jwt_service = jwt_service
        self.settings = get_settings()

    def login(
        self,
        request: LoginRequest,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> AuthResponse:
        login_id = helpers.normalize_code(request.login_id)
        validators.require_text(login_id, "loginId")
        validators.require_text(request.password, "password")

        user = self.user_repository.find_by_login_id(login_id)
        if user is None or not verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid loginId or password")
        self.ensure_account_is_active(user)
        return self.issue_session(user, user_agent=user_agent, ip_address=ip_address)

    def refresh(
        self,
        request: RefreshRequest,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> AuthResponse:
        validators.require_text(request.refresh_token, "refreshToken")
        now = utc_now()
        refresh_token = self.refresh_token_repository.find_active_by_token_hash(
            self.hash_refresh_token(request.refresh_token),
            now,
        )
        if refresh_token is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid or expired")

        user = self.user_repository.find_by_id(refresh_token.user_id)
        if user is None:
            self.refresh_token_repository.revoke(refresh_token, now)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid or expired")

        self.ensure_account_is_active(user)
        self.refresh_token_repository.revoke(refresh_token, now)
        return self.issue_session(user, user_agent=user_agent, ip_address=ip_address)

    def logout(self, request: LogoutRequest) -> None:
        validators.require_text(request.refresh_token, "refreshToken")
        refresh_token = self.refresh_token_repository.find_active_by_token_hash(
            self.hash_refresh_token(request.refresh_token),
            utc_now(),
        )
        if refresh_token is not None:
            self.refresh_token_repository.revoke(refresh_token, utc_now())

    def register_student(
        self,
        request: StudentRegistrationRequest,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> AuthResponse:
        student = self.resolve_registration_student(request)
        self.ensure_student_registration_matches(request, student)
        if self.user_repository.exists_by_student_id(student.student_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student already has a user account")

        login_id = helpers.normalize_code(request.login_id) or helpers.normalize_code(student.student_code)
        validators.require_text(login_id, "loginId")
        assert login_id is not None
        email = str(request.email).strip().lower()
        if self.user_repository.exists_by_login_id(login_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="loginId already exists")
        if self.user_repository.exists_by_email(email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

        user = User()
        user.login_id = login_id
        user.legacy_username = login_id
        user.password_hash = hash_password(request.password)
        user.email = email
        user.role = "Student"
        user.account_status = "ACTIVE"
        user.student_id = student.student_id
        self.user_repository.save(user)
        return self.issue_session(user, user_agent=user_agent, ip_address=ip_address)

    def issue_session(self, user: User, user_agent: str | None = None, ip_address: str | None = None) -> AuthResponse:
        access_token = self.jwt_service.generate_token(user.login_id, user.role)
        refresh_token_value = secrets.token_urlsafe(48)
        issued_at = utc_now()
        expires_at = issued_at + timedelta(minutes=self.settings.jwt_expiration_minutes)
        user.last_login_at = issued_at
        self.user_repository.save(user)

        refresh_token = RefreshToken()
        refresh_token.user_id = user.user_id
        refresh_token.token_hash = self.hash_refresh_token(refresh_token_value)
        refresh_token.user_agent = helpers.trim_to_none(user_agent)
        refresh_token.ip_address = helpers.trim_to_none(ip_address)
        refresh_token.issued_at = issued_at
        refresh_token.expires_at = issued_at + timedelta(days=self.settings.refresh_token_expiration_days)
        self.refresh_token_repository.save(refresh_token)
        self.refresh_token_repository.delete_expired(issued_at)
        self.refresh_token_repository.revoke_older_tokens(
            user.user_id,
            self.settings.max_active_refresh_tokens_per_user,
            issued_at,
        )

        return AuthResponse(
            token=access_token,
            access_token=access_token,
            refresh_token=refresh_token_value,
            issued_at=issued_at,
            expires_at=expires_at,
            user_id=user.user_id,
            login_id=user.login_id,
            username=user.login_id,
            email=user.email,
            role=user.role,
            student_id=user.student_id,
            teacher_id=user.teacher_id,
            staff_id=user.staff_id,
            profile_type=user.profile_type,
            profile_id=user.profile_id,
            account_status=user.account_status,
        )

    def ensure_account_is_active(self, user: User) -> None:
        status_value = (user.account_status or "").strip().upper()
        if status_value == "ACTIVE":
            return
        if status_value == "LOCKED":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is locked")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    def hash_refresh_token(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def resolve_registration_student(self, request: StudentRegistrationRequest) -> Student:
        student_repository = StudentRepository(self.user_repository.session)
        student = None
        if request.student_id is not None:
            student = student_repository.find_by_id(request.student_id)
            if student is not None and request.student_code is not None:
                requested_code = helpers.normalize_code(request.student_code)
                if helpers.normalize_code(student.student_code) != requested_code:
                    student = None
        elif request.student_code is not None:
            student = student_repository.find_by_student_code(helpers.normalize_code(request.student_code))

        if student is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student verification failed")
        return student

    def ensure_student_registration_matches(self, request: StudentRegistrationRequest, student: Student) -> None:
        requested_email = str(request.email).strip().lower()
        saved_email = (student.email or "").strip().lower()
        if requested_email != saved_email or request.dob != student.dob:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student verification failed")
