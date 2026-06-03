from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.common.pagination import PageResponse, paginate_items
from app.db.session import get_db_session
from app.modules.auth.authorization import AuthorizationService
from app.modules.auth.dependencies import get_current_user
from app.modules.marks.repository import StudentMarkRepository
from app.modules.marks.schemas import StudentMarkRead, StudentMarkWriteRequest
from app.modules.marks.service import StudentMarkService
from app.modules.students.repository import StudentRepository
from app.modules.subjects.repository import SubjectRepository
from app.modules.users.model import User


router = APIRouter(prefix="/api/marks", tags=["marks"], dependencies=[Depends(get_current_user)])


def get_student_mark_service(session: Session = Depends(get_db_session)) -> StudentMarkService:
    return StudentMarkService(StudentMarkRepository(session), StudentRepository(session), SubjectRepository(session))


def get_authorization_service(session: Session = Depends(get_db_session)) -> AuthorizationService:
    return AuthorizationService(session)


@router.get("", response_model=list[StudentMarkRead])
def get_marks(
    student_id: int | None = Query(default=None, alias="studentId"),
    subject_id: int | None = Query(default=None, alias="subjectId"),
    exam_type: str | None = Query(default=None, alias="examType"),
    sort_dir: str = Query(default="desc", alias="sortDir"),
    current_user: User = Depends(get_current_user),
    student_mark_service: StudentMarkService = Depends(get_student_mark_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> list[StudentMarkRead]:
    return resolve_mark_list(student_id, subject_id, exam_type, sort_dir, current_user, student_mark_service, authorization_service)


@router.get("/page", response_model=PageResponse[StudentMarkRead])
def get_marks_page(
    student_id: int | None = Query(default=None, alias="studentId"),
    subject_id: int | None = Query(default=None, alias="subjectId"),
    exam_type: str | None = Query(default=None, alias="examType"),
    sort_dir: str = Query(default="desc", alias="sortDir"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100, alias="pageSize"),
    current_user: User = Depends(get_current_user),
    student_mark_service: StudentMarkService = Depends(get_student_mark_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> PageResponse[StudentMarkRead]:
    return paginate_items(
        resolve_mark_list(student_id, subject_id, exam_type, sort_dir, current_user, student_mark_service, authorization_service),
        page,
        page_size,
    )


@router.get("/{mark_id}", response_model=StudentMarkRead)
def get_mark(
    mark_id: int,
    current_user: User = Depends(get_current_user),
    student_mark_service: StudentMarkService = Depends(get_student_mark_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> StudentMarkRead:
    mark = student_mark_service.find_mark(mark_id)
    student = student_mark_service.find_student(mark.student_id)
    subject = student_mark_service.find_subject(mark.subject_id)
    if authorization_service.is_student(current_user):
        authorization_service.ensure_student_access(current_user, student)
    elif authorization_service.is_teacher(current_user):
        if not authorization_service.can_access_student(current_user, student) or not authorization_service.can_access_subject(current_user, subject):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access is denied")
    elif not authorization_service.is_admin_or_staff(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access is denied")
    return student_mark_service.to_read(mark)


@router.post("", response_model=StudentMarkRead, status_code=status.HTTP_201_CREATED)
def create_mark(
    request: StudentMarkWriteRequest,
    current_user: User = Depends(get_current_user),
    student_mark_service: StudentMarkService = Depends(get_student_mark_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> StudentMarkRead:
    student = student_mark_service.find_student(request.student_id)
    subject = student_mark_service.find_subject(request.subject_id)
    authorization_service.ensure_mark_mutation_access(current_user, student, subject)
    return student_mark_service.create_mark(request)


@router.put("/{mark_id}", response_model=StudentMarkRead)
def update_mark(
    mark_id: int,
    request: StudentMarkWriteRequest,
    current_user: User = Depends(get_current_user),
    student_mark_service: StudentMarkService = Depends(get_student_mark_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> StudentMarkRead:
    student = student_mark_service.find_student(request.student_id)
    subject = student_mark_service.find_subject(request.subject_id)
    authorization_service.ensure_mark_mutation_access(current_user, student, subject)
    return student_mark_service.update_mark(mark_id, request)


@router.delete("/{mark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mark(
    mark_id: int,
    current_user: User = Depends(get_current_user),
    student_mark_service: StudentMarkService = Depends(get_student_mark_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> Response:
    mark = student_mark_service.find_mark(mark_id)
    student = student_mark_service.find_student(mark.student_id)
    subject = student_mark_service.find_subject(mark.subject_id)
    authorization_service.ensure_mark_mutation_access(current_user, student, subject)
    student_mark_service.delete_mark(mark_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def resolve_mark_list(
    student_id: int | None,
    subject_id: int | None,
    exam_type: str | None,
    sort_dir: str,
    current_user: User,
    student_mark_service: StudentMarkService,
    authorization_service: AuthorizationService,
) -> list[StudentMarkRead]:
    if authorization_service.is_admin_or_staff(current_user):
        return student_mark_service.get_marks(student_id, subject_id=subject_id, exam_type=exam_type, sort_dir=sort_dir)
    if authorization_service.is_student(current_user):
        current_student = authorization_service.require_current_student(current_user)
        if student_id is not None and student_id != current_student.student_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Students can only view their own marks")
        return student_mark_service.get_marks(current_student.student_id, subject_id=subject_id, exam_type=exam_type, sort_dir=sort_dir)
    if authorization_service.is_teacher(current_user):
        if student_id is not None:
            student = student_mark_service.find_student(student_id)
            authorization_service.ensure_student_access(current_user, student)
        if subject_id is not None:
            subject = student_mark_service.find_subject(subject_id)
            authorization_service.ensure_subject_access(current_user, subject)
        items = student_mark_service.get_marks(student_id, subject_id=subject_id, exam_type=exam_type, sort_dir=sort_dir)
        return [
            item
            for item in items
            if item.student_id is not None
            and item.subject_id is not None
            and authorization_service.can_access_student(current_user, student_mark_service.find_student(item.student_id))
            and authorization_service.can_access_subject(current_user, student_mark_service.find_subject(item.subject_id))
        ]
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access is denied")

