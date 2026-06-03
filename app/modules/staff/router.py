from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.modules.auth.authorization import AuthorizationService
from app.modules.auth.dependencies import get_current_user
from app.modules.staff.repository import StaffRepository
from app.modules.staff.schemas import StaffRead, StaffWriteRequest
from app.modules.staff.service import StaffService
from app.modules.users.model import User


router = APIRouter(prefix="/api/staff", tags=["staff"], dependencies=[Depends(get_current_user)])


def get_staff_service(session: Session = Depends(get_db_session)) -> StaffService:
    return StaffService(StaffRepository(session))


def get_authorization_service(session: Session = Depends(get_db_session)) -> AuthorizationService:
    return AuthorizationService(session)


@router.get("", response_model=list[StaffRead])
def get_staff_members(
    current_user: User = Depends(get_current_user),
    staff_service: StaffService = Depends(get_staff_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> list[StaffRead]:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can view staff records")
    return staff_service.get_staff_members()


@router.get("/{staff_id}", response_model=StaffRead)
def get_staff(
    staff_id: int,
    current_user: User = Depends(get_current_user),
    staff_service: StaffService = Depends(get_staff_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> StaffRead:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can view staff records")
    return staff_service.get_staff(staff_id)


@router.post("", response_model=StaffRead, status_code=status.HTTP_201_CREATED)
def create_staff(
    request: StaffWriteRequest,
    current_user: User = Depends(get_current_user),
    staff_service: StaffService = Depends(get_staff_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> StaffRead:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can create staff records")
    return staff_service.create_staff(request)


@router.put("/{staff_id}", response_model=StaffRead)
def update_staff(
    staff_id: int,
    request: StaffWriteRequest,
    current_user: User = Depends(get_current_user),
    staff_service: StaffService = Depends(get_staff_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> StaffRead:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can update staff records")
    return staff_service.update_staff(staff_id, request)


@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(
    staff_id: int,
    current_user: User = Depends(get_current_user),
    staff_service: StaffService = Depends(get_staff_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> Response:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can delete staff records")
    staff_service.delete_staff(staff_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
