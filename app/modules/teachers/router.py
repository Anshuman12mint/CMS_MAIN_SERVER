from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.common.pagination import PageResponse, paginate_items
from app.db.session import get_db_session
from app.modules.auth.authorization import AuthorizationService
from app.modules.auth.dependencies import get_current_user
from app.modules.courses.repository import CourseRepository
from app.modules.subjects.repository import SubjectRepository
from app.modules.teachers.repository import TeacherCourseRepository, TeacherRepository, TeacherSubjectRepository
from app.modules.teachers.schemas import CourseAssignmentRequest, SubjectAssignmentRequest, TeacherRead, TeacherWriteRequest
from app.modules.teachers.service import TeacherService
from app.modules.users.model import User


router = APIRouter(prefix="/api/teachers", tags=["teachers"], dependencies=[Depends(get_current_user)])


def get_teacher_service(session: Session = Depends(get_db_session)) -> TeacherService:
    return TeacherService(
        TeacherRepository(session),
        CourseRepository(session),
        SubjectRepository(session),
        TeacherCourseRepository(session),
        TeacherSubjectRepository(session),
    )


def get_authorization_service(session: Session = Depends(get_db_session)) -> AuthorizationService:
    return AuthorizationService(session)


@router.get("", response_model=list[TeacherRead])
def get_teachers(
    search: str | None = Query(default=None),
    sort_by: str | None = Query(default=None, alias="sortBy"),
    sort_dir: str = Query(default="asc", alias="sortDir"),
    current_user: User = Depends(get_current_user),
    teacher_service: TeacherService = Depends(get_teacher_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> list[TeacherRead]:
    teachers = teacher_service.get_teachers(search=search, sort_by=sort_by, sort_dir=sort_dir)
    return filter_teachers(current_user, teachers, authorization_service)


@router.get("/page", response_model=PageResponse[TeacherRead])
def get_teachers_page(
    search: str | None = Query(default=None),
    sort_by: str | None = Query(default=None, alias="sortBy"),
    sort_dir: str = Query(default="asc", alias="sortDir"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100, alias="pageSize"),
    current_user: User = Depends(get_current_user),
    teacher_service: TeacherService = Depends(get_teacher_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> PageResponse[TeacherRead]:
    teachers = teacher_service.get_teachers(search=search, sort_by=sort_by, sort_dir=sort_dir)
    return paginate_items(filter_teachers(current_user, teachers, authorization_service), page, page_size)


@router.get("/{teacher_id}", response_model=TeacherRead)
def get_teacher(
    teacher_id: int,
    current_user: User = Depends(get_current_user),
    teacher_service: TeacherService = Depends(get_teacher_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> TeacherRead:
    teacher = teacher_service.find_teacher(teacher_id)
    authorization_service.ensure_teacher_access(current_user, teacher)
    return teacher_service.to_read(teacher)


@router.post("", response_model=TeacherRead, status_code=status.HTTP_201_CREATED)
def create_teacher(
    request: TeacherWriteRequest,
    current_user: User = Depends(get_current_user),
    teacher_service: TeacherService = Depends(get_teacher_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> TeacherRead:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can create teachers")
    return teacher_service.create_teacher(request)


@router.put("/{teacher_id}", response_model=TeacherRead)
def update_teacher(
    teacher_id: int,
    request: TeacherWriteRequest,
    current_user: User = Depends(get_current_user),
    teacher_service: TeacherService = Depends(get_teacher_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> TeacherRead:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can update teachers")
    return teacher_service.update_teacher(teacher_id, request)


@router.put("/{teacher_id}/courses", response_model=TeacherRead)
def replace_teacher_courses(
    teacher_id: int,
    request: CourseAssignmentRequest,
    current_user: User = Depends(get_current_user),
    teacher_service: TeacherService = Depends(get_teacher_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> TeacherRead:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can manage teacher course assignments")
    return teacher_service.replace_courses(teacher_id, request.course_codes)


@router.put("/{teacher_id}/subjects", response_model=TeacherRead)
def replace_teacher_subjects(
    teacher_id: int,
    request: SubjectAssignmentRequest,
    current_user: User = Depends(get_current_user),
    teacher_service: TeacherService = Depends(get_teacher_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> TeacherRead:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can manage teacher subject assignments")
    return teacher_service.replace_subjects(teacher_id, request.subject_ids)


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(
    teacher_id: int,
    current_user: User = Depends(get_current_user),
    teacher_service: TeacherService = Depends(get_teacher_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> Response:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can delete teachers")
    teacher_service.delete_teacher(teacher_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def filter_teachers(
    current_user: User,
    teachers: list[TeacherRead],
    authorization_service: AuthorizationService,
) -> list[TeacherRead]:
    if authorization_service.is_admin_or_staff(current_user):
        return teachers
    if authorization_service.is_teacher(current_user):
        current_teacher = authorization_service.require_current_teacher(current_user)
        return [teacher for teacher in teachers if teacher.teacher_id == current_teacher.teacher_id]
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only staff, admins, or the owning teacher can view teacher records")
