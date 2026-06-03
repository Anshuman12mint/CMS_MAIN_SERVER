from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.modules.auth.authorization import AuthorizationService
from app.modules.auth.dependencies import get_current_user, require_roles
from app.modules.courses.repository import CourseRepository
from app.modules.subjects.repository import SubjectRepository
from app.modules.subjects.schemas import SubjectRead, SubjectWriteRequest
from app.modules.subjects.service import SubjectService
from app.modules.users.model import User


router = APIRouter(prefix="/api/subjects", tags=["subjects"], dependencies=[Depends(get_current_user)])


def get_subject_service(session: Session = Depends(get_db_session)) -> SubjectService:
    return SubjectService(SubjectRepository(session), CourseRepository(session))


def get_authorization_service(session: Session = Depends(get_db_session)) -> AuthorizationService:
    return AuthorizationService(session)


@router.get("", response_model=list[SubjectRead])
def get_subjects(
    course_code: str | None = Query(default=None, alias="courseCode"),
    current_user: User = Depends(get_current_user),
    subject_service: SubjectService = Depends(get_subject_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> list[SubjectRead]:
    subjects = subject_service.get_subjects(course_code)
    if authorization_service.is_admin_or_staff(current_user):
        return subjects
    return [
        subject_service.to_read(subject_service.find_subject(subject.subject_id))
        for subject in subjects
        if subject.subject_id is not None and authorization_service.can_access_subject(current_user, subject_service.find_subject(subject.subject_id))
    ]


@router.get("/{subject_id}", response_model=SubjectRead)
def get_subject(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    subject_service: SubjectService = Depends(get_subject_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> SubjectRead:
    subject = subject_service.find_subject(subject_id)
    if not authorization_service.can_access_subject(current_user, subject):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access is denied")
    return subject_service.to_read(subject)


@router.post(
    "",
    response_model=SubjectRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("Admin", "Staff"))],
)
def create_subject(
    request: SubjectWriteRequest,
    subject_service: SubjectService = Depends(get_subject_service),
) -> SubjectRead:
    return subject_service.create_subject(request)


@router.put(
    "/{subject_id}",
    response_model=SubjectRead,
    dependencies=[Depends(require_roles("Admin", "Staff"))],
)
def update_subject(
    subject_id: int,
    request: SubjectWriteRequest,
    subject_service: SubjectService = Depends(get_subject_service),
) -> SubjectRead:
    return subject_service.update_subject(subject_id, request)


@router.delete(
    "/{subject_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("Admin", "Staff"))],
)
def delete_subject(subject_id: int, subject_service: SubjectService = Depends(get_subject_service)) -> Response:
    subject_service.delete_subject(subject_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
