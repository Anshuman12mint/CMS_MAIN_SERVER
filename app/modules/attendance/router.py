from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.common.pagination import PageResponse, paginate_items
from app.db.session import get_db_session
from app.modules.attendance.repository import AttendanceRepository
from app.modules.attendance.schemas import AttendanceRead, AttendanceWriteRequest
from app.modules.attendance.service import AttendanceService
from app.modules.auth.authorization import AuthorizationService
from app.modules.auth.dependencies import get_current_user
from app.modules.students.repository import StudentRepository
from app.modules.users.model import User


router = APIRouter(prefix="/api/attendance", tags=["attendance"], dependencies=[Depends(get_current_user)])


def get_attendance_service(session: Session = Depends(get_db_session)) -> AttendanceService:
    return AttendanceService(AttendanceRepository(session), StudentRepository(session))


def get_authorization_service(session: Session = Depends(get_db_session)) -> AuthorizationService:
    return AuthorizationService(session)


@router.get("", response_model=list[AttendanceRead])
def get_attendance(
    student_id: int | None = Query(default=None, alias="studentId"),
    status_value: str | None = Query(default=None, alias="status"),
    sort_dir: str = Query(default="desc", alias="sortDir"),
    current_user: User = Depends(get_current_user),
    attendance_service: AttendanceService = Depends(get_attendance_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> list[AttendanceRead]:
    return resolve_attendance_list(student_id, status_value, sort_dir, current_user, attendance_service, authorization_service)


@router.get("/page", response_model=PageResponse[AttendanceRead])
def get_attendance_page(
    student_id: int | None = Query(default=None, alias="studentId"),
    status_value: str | None = Query(default=None, alias="status"),
    sort_dir: str = Query(default="desc", alias="sortDir"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100, alias="pageSize"),
    current_user: User = Depends(get_current_user),
    attendance_service: AttendanceService = Depends(get_attendance_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> PageResponse[AttendanceRead]:
    return paginate_items(
        resolve_attendance_list(student_id, status_value, sort_dir, current_user, attendance_service, authorization_service),
        page,
        page_size,
    )


@router.get("/{attendance_id}", response_model=AttendanceRead)
def get_attendance_by_id(
    attendance_id: int,
    current_user: User = Depends(get_current_user),
    attendance_service: AttendanceService = Depends(get_attendance_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> AttendanceRead:
    attendance = attendance_service.find_attendance(attendance_id)
    student = attendance_service.find_student(attendance.student_id)
    authorization_service.ensure_student_access(current_user, student)
    return attendance_service.to_read(attendance)


@router.post("", response_model=AttendanceRead, status_code=status.HTTP_201_CREATED)
def create_attendance(
    request: AttendanceWriteRequest,
    current_user: User = Depends(get_current_user),
    attendance_service: AttendanceService = Depends(get_attendance_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> AttendanceRead:
    student = attendance_service.find_student(request.student_id)
    authorization_service.ensure_attendance_mutation_access(current_user, student)
    return attendance_service.create_attendance(request)


@router.put("/{attendance_id}", response_model=AttendanceRead)
def update_attendance(
    attendance_id: int,
    request: AttendanceWriteRequest,
    current_user: User = Depends(get_current_user),
    attendance_service: AttendanceService = Depends(get_attendance_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> AttendanceRead:
    student = attendance_service.find_student(request.student_id)
    authorization_service.ensure_attendance_mutation_access(current_user, student)
    return attendance_service.update_attendance(attendance_id, request)


@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance(
    attendance_id: int,
    current_user: User = Depends(get_current_user),
    attendance_service: AttendanceService = Depends(get_attendance_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> Response:
    attendance = attendance_service.find_attendance(attendance_id)
    student = attendance_service.find_student(attendance.student_id)
    authorization_service.ensure_attendance_mutation_access(current_user, student)
    attendance_service.delete_attendance(attendance_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def resolve_attendance_list(
    student_id: int | None,
    status_value: str | None,
    sort_dir: str,
    current_user: User,
    attendance_service: AttendanceService,
    authorization_service: AuthorizationService,
) -> list[AttendanceRead]:
    if authorization_service.is_admin_or_staff(current_user):
        return attendance_service.get_attendance(student_id, status_value=status_value, sort_dir=sort_dir)
    if authorization_service.is_student(current_user):
        current_student = authorization_service.require_current_student(current_user)
        if student_id is not None and student_id != current_student.student_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Students can only view their own attendance")
        return attendance_service.get_attendance(current_student.student_id, status_value=status_value, sort_dir=sort_dir)
    if authorization_service.is_teacher(current_user):
        if student_id is not None:
            student = attendance_service.find_student(student_id)
            authorization_service.ensure_student_access(current_user, student)
            return attendance_service.get_attendance(student.student_id, status_value=status_value, sort_dir=sort_dir)
        items = attendance_service.get_attendance(None, status_value=status_value, sort_dir=sort_dir)
        return [
            item
            for item in items
            if item.student_id is not None
            and authorization_service.can_access_course(current_user, attendance_service.find_student(item.student_id).course_code)
        ]
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access is denied")

