from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.modules.admissions.schemas import AdmissionRead, AdmissionWriteRequest
from app.modules.admissions.service import AdmissionService
from app.modules.auth.authorization import AuthorizationService
from app.modules.auth.dependencies import get_current_user
from app.modules.courses.repository import CourseRepository
from app.modules.students.repository import StudentRepository
from app.modules.students.service import StudentService
from app.modules.users.model import User


router = APIRouter(prefix="/api/admissions", tags=["admissions"], dependencies=[Depends(get_current_user)])


def get_admission_service(session: Session = Depends(get_db_session)) -> AdmissionService:
    return AdmissionService(StudentService(StudentRepository(session), CourseRepository(session)))


def get_authorization_service(session: Session = Depends(get_db_session)) -> AuthorizationService:
    return AuthorizationService(session)


@router.get("", response_model=list[AdmissionRead])
def get_admissions(
    current_user: User = Depends(get_current_user),
    admission_service: AdmissionService = Depends(get_admission_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> list[AdmissionRead]:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can view admissions")
    return admission_service.get_admissions()


@router.get("/{student_id}", response_model=AdmissionRead)
def get_admission(
    student_id: int,
    current_user: User = Depends(get_current_user),
    admission_service: AdmissionService = Depends(get_admission_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> AdmissionRead:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can view admissions")
    return admission_service.get_admission(student_id)


@router.post("", response_model=AdmissionRead, status_code=status.HTTP_201_CREATED)
def create_admission(
    request: AdmissionWriteRequest,
    current_user: User = Depends(get_current_user),
    admission_service: AdmissionService = Depends(get_admission_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> AdmissionRead:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can create admissions")
    return admission_service.create_admission(request)


@router.put("/{student_id}", response_model=AdmissionRead)
def update_admission(
    student_id: int,
    request: AdmissionWriteRequest,
    current_user: User = Depends(get_current_user),
    admission_service: AdmissionService = Depends(get_admission_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> AdmissionRead:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can update admissions")
    return admission_service.update_admission(student_id, request)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admission(
    student_id: int,
    current_user: User = Depends(get_current_user),
    admission_service: AdmissionService = Depends(get_admission_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> Response:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can delete admissions")
    admission_service.delete_admission(student_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
