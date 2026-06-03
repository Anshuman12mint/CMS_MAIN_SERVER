from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.modules.auth.authorization import AuthorizationService
from app.modules.auth.dependencies import get_current_user, require_roles
from app.modules.courses.repository import CourseRepository
from app.modules.courses.schemas import CourseRead, CourseWriteRequest
from app.modules.courses.service import CourseService
from app.modules.users.model import User


router = APIRouter(prefix="/api/courses", tags=["courses"], dependencies=[Depends(get_current_user)])


def get_course_service(session: Session = Depends(get_db_session)) -> CourseService:
    return CourseService(CourseRepository(session))


def get_authorization_service(session: Session = Depends(get_db_session)) -> AuthorizationService:
    return AuthorizationService(session)


@router.get("", response_model=list[CourseRead])
def get_courses(
    current_user: User = Depends(get_current_user),
    course_service: CourseService = Depends(get_course_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> list[CourseRead]:
    courses = course_service.get_courses()
    if authorization_service.is_admin_or_staff(current_user):
        return courses
    return [course for course in courses if authorization_service.can_access_course(current_user, course.course_code)]


@router.get("/{course_code}", response_model=CourseRead)
def get_course(
    course_code: str,
    current_user: User = Depends(get_current_user),
    course_service: CourseService = Depends(get_course_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> CourseRead:
    if not authorization_service.can_access_course(current_user, course_code):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access is denied")
    return course_service.get_course(course_code)


@router.post(
    "",
    response_model=CourseRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("Admin", "Staff"))],
)
def create_course(
    request: CourseWriteRequest,
    course_service: CourseService = Depends(get_course_service),
) -> CourseRead:
    return course_service.create_course(request)


@router.put(
    "/{course_code}",
    response_model=CourseRead,
    dependencies=[Depends(require_roles("Admin", "Staff"))],
)
def update_course(
    course_code: str,
    request: CourseWriteRequest,
    course_service: CourseService = Depends(get_course_service),
) -> CourseRead:
    return course_service.update_course(course_code, request)


@router.delete(
    "/{course_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("Admin", "Staff"))],
)
def delete_course(course_code: str, course_service: CourseService = Depends(get_course_service)) -> Response:
    course_service.delete_course(course_code)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
