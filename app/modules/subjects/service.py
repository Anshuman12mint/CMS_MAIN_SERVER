from __future__ import annotations

from fastapi import HTTPException, status

from app.common import helpers, validators
from app.modules.courses.repository import CourseRepository
from app.modules.subjects.model import Subject
from app.modules.subjects.repository import SubjectRepository
from app.modules.subjects.schemas import SubjectRead, SubjectWriteRequest


class SubjectService:
    def __init__(self, subject_repository: SubjectRepository, course_repository: CourseRepository) -> None:
        self.subject_repository = subject_repository
        self.course_repository = course_repository

    def get_subjects(self, course_code: str | None = None) -> list[SubjectRead]:
        normalized_course_code = helpers.normalize_code(course_code)
        subjects = (
            self.subject_repository.find_by_course_code(normalized_course_code)
            if normalized_course_code is not None
            else self.subject_repository.find_all()
        )
        return [self.to_read(subject) for subject in subjects]

    def get_subject(self, subject_id: int) -> SubjectRead:
        return self.to_read(self.find_subject(subject_id))

    def create_subject(self, request: SubjectWriteRequest) -> SubjectRead:
        subject = Subject()
        self.apply_subject(subject, request, current_subject_id=None)
        return self.to_read(self.subject_repository.save(subject))

    def update_subject(self, subject_id: int, request: SubjectWriteRequest) -> SubjectRead:
        subject = self.find_subject(subject_id)
        self.apply_subject(subject, request, current_subject_id=subject.subject_id)
        return self.to_read(self.subject_repository.save(subject))

    def delete_subject(self, subject_id: int) -> None:
        self.subject_repository.delete(self.find_subject(subject_id))

    def find_subject(self, subject_id: int | None) -> Subject:
        subject = self.subject_repository.find_by_id(subject_id)
        if subject is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        return subject

    def apply_subject(self, subject: Subject, request: SubjectWriteRequest, current_subject_id: int | None) -> None:
        subject_name = helpers.trim_to_none(request.subject_name)
        subject_code = helpers.normalize_code(request.subject_code)
        course_code = helpers.normalize_code(request.course_code)
        validators.require_text(subject_name, "subjectName")
        validators.require_text(subject_code, "subjectCode")
        validators.require_text(course_code, "courseCode")
        assert subject_name is not None
        assert subject_code is not None
        assert course_code is not None

        if not self.course_repository.exists_by_id(course_code):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        if self.subject_repository.exists_by_subject_code(subject_code, exclude_subject_id=current_subject_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="subjectCode already exists")

        subject.subject_name = subject_name
        subject.subject_code = subject_code
        subject.course_code = course_code
        subject.subject_description = helpers.trim_to_none(request.subject_description)

    def to_read(self, subject: Subject) -> SubjectRead:
        return SubjectRead(
            subject_id=subject.subject_id,
            subject_name=subject.subject_name,
            subject_code=subject.subject_code,
            course_code=subject.course_code,
            subject_description=subject.subject_description,
        )

