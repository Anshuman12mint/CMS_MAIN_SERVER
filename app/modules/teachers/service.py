from __future__ import annotations

import secrets

from fastapi import HTTPException, status

from app.common import helpers, validators
from app.modules.courses.repository import CourseRepository
from app.modules.subjects.repository import SubjectRepository
from app.modules.teachers.model import Teacher, TeacherCourse, TeacherSubject
from app.modules.teachers.repository import TeacherCourseRepository, TeacherRepository, TeacherSubjectRepository
from app.modules.teachers.schemas import TeacherRead, TeacherWriteRequest


class TeacherService:
    def __init__(
        self,
        teacher_repository: TeacherRepository,
        course_repository: CourseRepository,
        subject_repository: SubjectRepository,
        teacher_course_repository: TeacherCourseRepository,
        teacher_subject_repository: TeacherSubjectRepository,
    ) -> None:
        self.teacher_repository = teacher_repository
        self.course_repository = course_repository
        self.subject_repository = subject_repository
        self.teacher_course_repository = teacher_course_repository
        self.teacher_subject_repository = teacher_subject_repository

    def get_teachers(self, search: str | None = None, sort_by: str | None = None, sort_dir: str = "asc") -> list[TeacherRead]:
        items = [self.to_read(teacher) for teacher in self.teacher_repository.find_all()]
        if validators.has_text(search):
            query = search.strip().lower()
            items = [
                teacher
                for teacher in items
                if query in " ".join(
                    [
                        teacher.first_name or "",
                        teacher.last_name or "",
                        teacher.teacher_code or "",
                        teacher.email or "",
                        teacher.department or "",
                    ]
                ).lower()
            ]
        return self.sort_teachers(items, sort_by, sort_dir)

    def get_teacher(self, teacher_id: int) -> TeacherRead:
        return self.to_read(self.find_teacher(teacher_id))

    def create_teacher(self, request: TeacherWriteRequest) -> TeacherRead:
        teacher = Teacher()
        self.apply_teacher(teacher, request)
        saved_teacher = self.teacher_repository.save(teacher)
        self.sync_assignments(saved_teacher, request.course_codes, request.subject_ids)
        return self.get_teacher(saved_teacher.teacher_id)

    def update_teacher(self, teacher_id: int, request: TeacherWriteRequest) -> TeacherRead:
        teacher = self.find_teacher(teacher_id)
        self.apply_teacher(teacher, request)
        self.teacher_repository.save(teacher)
        if request.course_codes is not None or request.subject_ids is not None:
            self.sync_assignments(teacher, request.course_codes, request.subject_ids)
        return self.get_teacher(teacher_id)

    def delete_teacher(self, teacher_id: int) -> None:
        teacher = self.find_teacher(teacher_id)
        self.teacher_course_repository.delete_by_teacher_id(teacher.teacher_id)
        self.teacher_subject_repository.delete_by_teacher_id(teacher.teacher_id)
        self.teacher_repository.delete(teacher)

    def replace_courses(self, teacher_id: int, course_codes: list[str] | None) -> TeacherRead:
        teacher = self.find_teacher(teacher_id)
        self.sync_courses(teacher, course_codes)
        return self.get_teacher(teacher_id)

    def replace_subjects(self, teacher_id: int, subject_ids: list[int] | None) -> TeacherRead:
        teacher = self.find_teacher(teacher_id)
        self.sync_subjects(teacher, subject_ids)
        return self.get_teacher(teacher_id)

    def find_teacher(self, teacher_id: int | None) -> Teacher:
        teacher = self.teacher_repository.find_by_id(teacher_id)
        if teacher is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
        return teacher

    def apply_teacher(self, teacher: Teacher, request: TeacherWriteRequest) -> None:
        validators.require_text(request.first_name, "firstName")
        validators.require_text(request.last_name, "lastName")
        validators.require(request.dob is not None, "dob is required")
        validators.require(request.hire_date is not None, "hireDate is required")
        validators.require_text(request.phone_number, "phoneNumber")
        validators.require_text(str(request.email) if request.email is not None else None, "email")
        teacher_code = helpers.normalize_code(request.teacher_code) or teacher.teacher_code or self.generate_teacher_code(teacher.teacher_id)
        if self.teacher_repository.exists_by_teacher_code(teacher_code, exclude_teacher_id=teacher.teacher_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="teacherCode already exists")

        assert request.dob is not None
        assert request.hire_date is not None
        teacher.teacher_code = teacher_code
        teacher.first_name = helpers.trim_to_none(request.first_name) or ""
        teacher.last_name = helpers.trim_to_none(request.last_name) or ""
        teacher.dob = request.dob
        teacher.gender = validators.normalize_required_choice(request.gender, validators.GENDERS, "gender")
        teacher.phone_number = helpers.trim_to_none(request.phone_number) or ""
        teacher.email = str(request.email).lower()
        teacher.hire_date = request.hire_date
        teacher.department = helpers.trim_to_none(request.department)
        teacher.address = helpers.trim_to_none(request.address)
        teacher.qualification = helpers.trim_to_none(request.qualification)
        teacher.salary = request.salary

    def generate_teacher_code(self, teacher_id: int | None) -> str:
        if teacher_id is not None:
            return f"TCH-{teacher_id:05d}"
        while True:
            candidate = "TCH-" + secrets.token_hex(4).upper()
            if not self.teacher_repository.exists_by_teacher_code(candidate):
                return candidate

    def sync_assignments(self, teacher: Teacher, course_codes: list[str] | None, subject_ids: list[int] | None) -> None:
        if course_codes is not None:
            self.sync_courses(teacher, course_codes)
        if subject_ids is not None:
            self.sync_subjects(teacher, subject_ids)

    def sync_courses(self, teacher: Teacher, course_codes: list[str] | None) -> None:
        self.teacher_course_repository.delete_by_teacher_id(teacher.teacher_id)
        assignments: list[TeacherCourse] = []
        for course_code in helpers.distinct_list(helpers.normalize_code(item) for item in (course_codes or [])):
            course = self.course_repository.find_by_id(course_code)
            if course is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
            assignment = TeacherCourse()
            assignment.teacher_id = teacher.teacher_id
            assignment.course_code = course.course_code
            assignments.append(assignment)
        self.teacher_course_repository.save_all(assignments)

    def sync_subjects(self, teacher: Teacher, subject_ids: list[int] | None) -> None:
        self.teacher_subject_repository.delete_by_teacher_id(teacher.teacher_id)
        assignments: list[TeacherSubject] = []
        for subject_id in helpers.distinct_list(subject_ids):
            subject = self.subject_repository.find_by_id(subject_id)
            if subject is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
            assignment = TeacherSubject()
            assignment.teacher_id = teacher.teacher_id
            assignment.subject_id = subject.subject_id
            assignments.append(assignment)
        self.teacher_subject_repository.save_all(assignments)

    def sort_teachers(self, teachers: list[TeacherRead], sort_by: str | None, sort_dir: str) -> list[TeacherRead]:
        normalized_sort_by = (sort_by or "lastName").strip()
        reverse = (sort_dir or "asc").strip().lower() == "desc"
        key_map = {
            "createdAt": lambda teacher: (teacher.created_at is None, teacher.created_at),
            "hireDate": lambda teacher: (teacher.hire_date is None, teacher.hire_date),
            "firstName": lambda teacher: (teacher.first_name or "").lower(),
            "lastName": lambda teacher: (teacher.last_name or "").lower(),
            "teacherCode": lambda teacher: (teacher.teacher_code or "").lower(),
        }
        return sorted(teachers, key=key_map.get(normalized_sort_by, key_map["lastName"]), reverse=reverse)

    def to_read(self, teacher: Teacher) -> TeacherRead:
        course_codes = [assignment.course_code for assignment in self.teacher_course_repository.find_by_teacher_id(teacher.teacher_id)]
        subject_ids = [assignment.subject_id for assignment in self.teacher_subject_repository.find_by_teacher_id(teacher.teacher_id)]
        return TeacherRead(
            teacher_id=teacher.teacher_id,
            teacher_code=teacher.teacher_code,
            first_name=teacher.first_name,
            last_name=teacher.last_name,
            dob=teacher.dob,
            gender=teacher.gender,
            phone_number=teacher.phone_number,
            email=teacher.email,
            hire_date=teacher.hire_date,
            department=teacher.department,
            address=teacher.address,
            qualification=teacher.qualification,
            salary=teacher.salary,
            course_codes=course_codes,
            subject_ids=subject_ids,
            created_at=teacher.created_at,
        )

