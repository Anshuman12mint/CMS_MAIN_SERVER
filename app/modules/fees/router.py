from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.common.pagination import PageResponse, paginate_items
from app.db.session import get_db_session
from app.modules.auth.authorization import AuthorizationService
from app.modules.auth.dependencies import get_current_user
from app.modules.fees.repository import FeeRepository
from app.modules.fees.schemas import FeeRead, FeeWriteRequest
from app.modules.fees.service import FeeService
from app.modules.students.repository import StudentRepository
from app.modules.users.model import User


router = APIRouter(prefix="/api/fees", tags=["fees"], dependencies=[Depends(get_current_user)])


def get_fee_service(session: Session = Depends(get_db_session)) -> FeeService:
    return FeeService(FeeRepository(session), StudentRepository(session))


def get_authorization_service(session: Session = Depends(get_db_session)) -> AuthorizationService:
    return AuthorizationService(session)


@router.get("", response_model=list[FeeRead])
def get_fees(
    student_id: int | None = Query(default=None, alias="studentId"),
    status_value: str | None = Query(default=None, alias="status"),
    sort_dir: str = Query(default="desc", alias="sortDir"),
    current_user: User = Depends(get_current_user),
    fee_service: FeeService = Depends(get_fee_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> list[FeeRead]:
    return resolve_fee_list(student_id, status_value, sort_dir, current_user, fee_service, authorization_service)


@router.get("/page", response_model=PageResponse[FeeRead])
def get_fees_page(
    student_id: int | None = Query(default=None, alias="studentId"),
    status_value: str | None = Query(default=None, alias="status"),
    sort_dir: str = Query(default="desc", alias="sortDir"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100, alias="pageSize"),
    current_user: User = Depends(get_current_user),
    fee_service: FeeService = Depends(get_fee_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> PageResponse[FeeRead]:
    return paginate_items(resolve_fee_list(student_id, status_value, sort_dir, current_user, fee_service, authorization_service), page, page_size)


@router.get("/{fee_id}", response_model=FeeRead)
def get_fee(
    fee_id: int,
    current_user: User = Depends(get_current_user),
    fee_service: FeeService = Depends(get_fee_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> FeeRead:
    fee = fee_service.find_fee(fee_id)
    student = fee_service.find_student(fee.student_id)
    authorization_service.ensure_fee_student_access(current_user, student)
    return fee_service.to_read(fee)


@router.post("", response_model=FeeRead, status_code=status.HTTP_201_CREATED)
def create_fee(
    request: FeeWriteRequest,
    current_user: User = Depends(get_current_user),
    fee_service: FeeService = Depends(get_fee_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> FeeRead:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can create fees")
    return fee_service.create_fee(request)


@router.put("/{fee_id}", response_model=FeeRead)
def update_fee(
    fee_id: int,
    request: FeeWriteRequest,
    current_user: User = Depends(get_current_user),
    fee_service: FeeService = Depends(get_fee_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> FeeRead:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can update fees")
    return fee_service.update_fee(fee_id, request)


@router.delete("/{fee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fee(
    fee_id: int,
    current_user: User = Depends(get_current_user),
    fee_service: FeeService = Depends(get_fee_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> Response:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can delete fees")
    fee_service.delete_fee(fee_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def resolve_fee_list(
    student_id: int | None,
    status_value: str | None,
    sort_dir: str,
    current_user: User,
    fee_service: FeeService,
    authorization_service: AuthorizationService,
) -> list[FeeRead]:
    if authorization_service.is_admin_or_staff(current_user):
        return fee_service.get_fees(student_id, status_value=status_value, sort_dir=sort_dir)
    if authorization_service.is_student(current_user):
        current_student = authorization_service.require_current_student(current_user)
        if student_id is not None and student_id != current_student.student_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Students can only view their own fees")
        return fee_service.get_fees(current_student.student_id, status_value=status_value, sort_dir=sort_dir)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only staff, admins, or the owning student can view fees")

