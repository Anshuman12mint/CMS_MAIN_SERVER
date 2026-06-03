from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.jwt import JwtService
from app.modules.auth.rate_limiter import login_rate_limiter
from app.modules.auth.refresh_token_repository import RefreshTokenRepository
from app.modules.auth.schemas import AuthResponse, LoginRequest, LogoutRequest, RefreshRequest, StudentRegistrationRequest
from app.modules.auth.service import AuthService
from app.modules.users.model import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserRead

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_auth_service(session: Session = Depends(get_db_session)) -> AuthService:
    return AuthService(UserRepository(session), RefreshTokenRepository(session), JwtService())


@router.post("/login", response_model=AuthResponse)
def login(
    request: LoginRequest,
    http_request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    rate_limit_key = build_rate_limit_key(request.login_id or request.username or "", http_request)
    login_rate_limiter.ensure_allowed(rate_limit_key)
    try:
        response = auth_service.login(
            request,
            user_agent=http_request.headers.get("user-agent"),
            ip_address=http_request.client.host if http_request.client is not None else None,
        )
    except HTTPException as exc:
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            login_rate_limiter.record_failure(rate_limit_key)
        raise
    login_rate_limiter.record_success(rate_limit_key)
    return response


@router.post("/refresh", response_model=AuthResponse)
def refresh(
    request: RefreshRequest,
    http_request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    return auth_service.refresh(
        request,
        user_agent=http_request.headers.get("user-agent"),
        ip_address=http_request.client.host if http_request.client is not None else None,
    )


@router.post("/register/student", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register_student(
    request: StudentRegistrationRequest,
    http_request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    return auth_service.register_student(
        request,
        user_agent=http_request.headers.get("user-agent"),
        ip_address=http_request.client.host if http_request.client is not None else None,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: LogoutRequest, auth_service: AuthService = Depends(get_auth_service)) -> None:
    auth_service.logout(request)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead(
        user_id=current_user.user_id,
        login_id=current_user.login_id,
        username=current_user.login_id,
        email=current_user.email,
        role=current_user.role,
        student_id=current_user.student_id,
        teacher_id=current_user.teacher_id,
        staff_id=current_user.staff_id,
        profile_type=current_user.profile_type,
        profile_id=current_user.profile_id,
        account_status=current_user.account_status,
        registered_at=current_user.registered_at,
        last_login_at=current_user.last_login_at,
        created_at=current_user.created_at,
    )


def build_rate_limit_key(login_id: str, request: Request) -> str:
    normalized_login_id = (login_id or "").strip().lower()
    remote_address = request.client.host if request.client is not None else "unknown"
    return f"{normalized_login_id}|{remote_address}"
