from __future__ import annotations

from fastapi import HTTPException, status

from app.common import helpers, validators
from app.modules.marks.model import StudentMark
from app.modules.marks.repository import StudentMarkRepository
from app.modules.marks.schemas import StudentMarkRead, StudentMarkWriteRequest
from app.modules.students.model import Student
from app.modules.students.repository import StudentRepository
from app.modules.subjects.model import Subject
from app.modules.subjects.repository import SubjectRepository


class StudentMarkService:
    def __init__(
        self,
        student_mark_repository: StudentMarkRepository,
        student_repository: StudentRepository,
        subject_repository: SubjectRepository,
    ) -> None:
        self.student_mark_repository = student_mark_repository
        self.student_repository = student_repository
        self.subject_repository = subject_repository

    def get_marks(
        self,
        student_id: int | None,
        subject_id: int | None = None,
        exam_type: str | None = None,
        sort_dir: str = "desc",
    ) -> list[StudentMarkRead]:
        rows = (
            self.student_mark_repository.find_all_ordered()
            if student_id is None
            else self.student_mark_repository.find_by_student_id_ordered(student_id)
        )
        items = [self.to_read(row) for row in rows]
        if subject_id is not None:
            items = [item for item in items if item.subject_id == subject_id]
        if validators.has_text(exam_type):
            normalized_exam_type = exam_type.strip().lower()
            items = [item for item in items if (item.exam_type or "").strip().lower() == normalized_exam_type]
        return items if (sort_dir or "desc").strip().lower() != "asc" else list(reversed(items))

    def get_mark(self, mark_id: int) -> StudentMarkRead:
        return self.to_read(self.find_mark(mark_id))

    def create_mark(self, request: StudentMarkWriteRequest) -> StudentMarkRead:
        mark = StudentMark()
        self.apply_mark(mark, request)
        return self.to_read(self.student_mark_repository.save(mark))

    def update_mark(self, mark_id: int, request: StudentMarkWriteRequest) -> StudentMarkRead:
        mark = self.find_mark(mark_id)
        self.apply_mark(mark, request)
        return self.to_read(self.student_mark_repository.save(mark))

    def delete_mark(self, mark_id: int) -> None:
        self.student_mark_repository.delete(self.find_mark(mark_id))

    def apply_mark(self, mark: StudentMark, request: StudentMarkWriteRequest) -> None:
        student = self.find_student(request.student_id)
        subject = self.find_subject(request.subject_id)
        validators.require(request.semester is not None, "semester is required")
        validators.require(request.exam_date is not None, "examDate is required")
        validators.require(request.marks_obtained is not None, "marksObtained is required")
        validators.require(request.max_marks is not None, "maxMarks is required")
        assert request.semester is not None
        assert request.exam_date is not None
        assert request.marks_obtained is not None
        assert request.max_marks is not None
        mark.student = student
        mark.student_id = student.student_id
        mark.subject = subject
        mark.subject_id = subject.subject_id
        mark.semester = request.semester
        mark.exam_type = validators.normalize_required_choice(request.exam_type, validators.EXAM_TYPES, "examType")
        mark.marks_obtained = request.marks_obtained
        mark.max_marks = request.max_marks
        mark.grade = helpers.trim_to_none(request.grade)
        mark.exam_date = request.exam_date

    def find_mark(self, mark_id: int | None) -> StudentMark:
        mark = self.student_mark_repository.find_by_id(mark_id)
        if mark is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mark not found")
        return mark

    def find_student(self, student_id: int | None) -> Student:
        student = self.student_repository.find_by_id(student_id)
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return student

    def find_subject(self, subject_id: int | None) -> Subject:
        subject = self.subject_repository.find_by_id(subject_id)
        if subject is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        return subject

    def to_read(self, mark: StudentMark) -> StudentMarkRead:
        return StudentMarkRead(
            mark_id=mark.mark_id,
            student_id=mark.student.student_id if mark.student is not None else mark.student_id,
            subject_id=mark.subject.subject_id if mark.subject is not None else mark.subject_id,
            semester=mark.semester,
            exam_type=mark.exam_type,
            marks_obtained=mark.marks_obtained,
            max_marks=mark.max_marks,
            grade=mark.grade,
            exam_date=mark.exam_date,
        )

