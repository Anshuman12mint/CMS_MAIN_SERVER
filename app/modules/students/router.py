from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.common.pagination import PageResponse, paginate_items
from app.db.session import get_db_session
from app.modules.auth.authorization import AuthorizationService
from app.modules.auth.dependencies import get_current_user
from app.modules.courses.repository import CourseRepository
from app.modules.students.repository import StudentRepository
from app.modules.students.schemas import StudentRead, StudentWriteRequest
from app.modules.students.service import StudentService
from app.modules.users.model import User


router = APIRouter(prefix="/api/students", tags=["students"], dependencies=[Depends(get_current_user)])


def get_student_service(session: Session = Depends(get_db_session)) -> StudentService:
    return StudentService(StudentRepository(session), CourseRepository(session))


def get_authorization_service(session: Session = Depends(get_db_session)) -> AuthorizationService:
    return AuthorizationService(session)


@router.get("", response_model=list[StudentRead])
def get_students(
    course_code: str | None = Query(default=None, alias="courseCode"),
    search: str | None = Query(default=None),
    sort_by: str | None = Query(default=None, alias="sortBy"),
    sort_dir: str = Query(default="desc", alias="sortDir"),
    current_user: User = Depends(get_current_user),
    student_service: StudentService = Depends(get_student_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> list[StudentRead]:
    students = student_service.get_students(course_code, search=search, sort_by=sort_by, sort_dir=sort_dir)
    return filter_student_list(current_user, students, authorization_service)


@router.get("/page", response_model=PageResponse[StudentRead])
def get_students_page(
    course_code: str | None = Query(default=None, alias="courseCode"),
    search: str | None = Query(default=None),
    sort_by: str | None = Query(default=None, alias="sortBy"),
    sort_dir: str = Query(default="desc", alias="sortDir"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100, alias="pageSize"),
    current_user: User = Depends(get_current_user),
    student_service: StudentService = Depends(get_student_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> PageResponse[StudentRead]:
    students = student_service.get_students(course_code, search=search, sort_by=sort_by, sort_dir=sort_dir)
    return paginate_items(filter_student_list(current_user, students, authorization_service), page, page_size)


@router.get("/{student_id}", response_model=StudentRead)
def get_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    student_service: StudentService = Depends(get_student_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> StudentRead:
    student = student_service.find_student(student_id)
    authorization_service.ensure_student_access(current_user, student)
    return student_service.to_read(student)


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(
    request: StudentWriteRequest,
    current_user: User = Depends(get_current_user),
    student_service: StudentService = Depends(get_student_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> StudentRead:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can create students")
    return student_service.create_student(request)


@router.put("/{student_id}", response_model=StudentRead)
def update_student(
    student_id: int,
    request: StudentWriteRequest,
    current_user: User = Depends(get_current_user),
    student_service: StudentService = Depends(get_student_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> StudentRead:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can update students")
    return student_service.update_student(student_id, request)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    student_service: StudentService = Depends(get_student_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> Response:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can delete students")
    student_service.delete_student(student_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def filter_student_list(
    current_user: User,
    students: list[StudentRead],
    authorization_service: AuthorizationService,
) -> list[StudentRead]:
    if authorization_service.is_admin_or_staff(current_user):
        return students
    if authorization_service.is_teacher(current_user):
        return [student for student in students if authorization_service.can_access_course(current_user, student.course_code)]
    if authorization_service.is_student(current_user):
        current_student = authorization_service.require_current_student(current_user)
        return [student for student in students if student.student_id == current_student.student_id]
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access is denied")
