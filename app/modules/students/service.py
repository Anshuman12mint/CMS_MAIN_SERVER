from __future__ import annotations

import secrets

from fastapi import HTTPException, status

from app.common import helpers, validators
from app.modules.courses.repository import CourseRepository
from app.modules.students.model import Student
from app.modules.students.repository import StudentRepository
from app.modules.students.schemas import StudentRead, StudentWriteRequest


class StudentService:
    def __init__(self, student_repository: StudentRepository, course_repository: CourseRepository) -> None:
        self.student_repository = student_repository
        self.course_repository = course_repository

    def get_students(
        self,
        course_code: str | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_dir: str = "desc",
    ) -> list[StudentRead]:
        normalized_course_code = helpers.normalize_code(course_code)
        students = (
            self.student_repository.find_by_course_code_ordered(normalized_course_code)
            if normalized_course_code is not None
            else self.student_repository.find_all_ordered()
        )
        items = [self.to_read(student) for student in students]
        if validators.has_text(search):
            query = search.strip().lower()
            items = [
                student
                for student in items
                if query in " ".join(
                    [
                        student.first_name or "",
                        student.last_name or "",
                        student.student_code or "",
                        student.email or "",
                        student.phone_number or "",
                        student.course_code or "",
                    ]
                ).lower()
            ]
        return self.sort_students(items, sort_by, sort_dir)

    def get_student(self, student_id: int) -> StudentRead:
        return self.to_read(self.find_student(student_id))

    def create_student(self, request: StudentWriteRequest) -> StudentRead:
        student = Student()
        self.apply_student(student, request)
        return self.to_read(self.student_repository.save(student))

    def update_student(self, student_id: int, request: StudentWriteRequest) -> StudentRead:
        student = self.find_student(student_id)
        self.apply_student(student, request)
        return self.to_read(self.student_repository.save(student))

    def delete_student(self, student_id: int) -> None:
        self.student_repository.delete(self.find_student(student_id))

    def find_student(self, student_id: int | None) -> Student:
        student = self.student_repository.find_by_id(student_id)
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return student

    def apply_student(self, student: Student, request: StudentWriteRequest) -> None:
        validators.require_text(request.first_name, "firstName")
        validators.require_text(request.last_name, "lastName")
        validators.require(request.dob is not None, "dob is required")
        validators.require(request.admission_date is not None, "admissionDate is required")
        validators.require_text(request.phone_number, "phoneNumber")
        validators.require_text(str(request.email) if request.email is not None else None, "email")
        validators.require_text(request.course_code, "courseCode")

        course_code = helpers.normalize_code(request.course_code)
        if not self.course_repository.exists_by_id(course_code):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        student_code = helpers.normalize_code(request.student_code) or student.student_code or self.generate_student_code(student.student_id)
        if self.student_repository.exists_by_student_code(student_code, exclude_student_id=student.student_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="studentCode already exists")

        assert course_code is not None
        assert request.dob is not None
        assert request.admission_date is not None
        student.student_code = student_code
        student.first_name = helpers.trim_to_none(request.first_name) or ""
        student.last_name = helpers.trim_to_none(request.last_name) or ""
        student.dob = request.dob
        student.gender = validators.normalize_required_choice(request.gender, validators.GENDERS, "gender")
        student.phone_number = helpers.trim_to_none(request.phone_number) or ""
        student.email = str(request.email).lower()
        student.course_code = course_code
        student.admission_date = request.admission_date
        student.address = helpers.trim_to_none(request.address)
        student.guardian_name = helpers.trim_to_none(request.guardian_name)
        student.guardian_contact = helpers.trim_to_none(request.guardian_contact)
        student.blood_group = validators.normalize_optional_choice(request.blood_group, validators.BLOOD_GROUPS, "bloodGroup")

    def generate_student_code(self, student_id: int | None) -> str:
        if student_id is not None:
            return f"STU-{student_id:05d}"
        while True:
            candidate = "STU-" + secrets.token_hex(4).upper()
            if not self.student_repository.exists_by_student_code(candidate):
                return candidate

    def sort_students(self, students: list[StudentRead], sort_by: str | None, sort_dir: str) -> list[StudentRead]:
        normalized_sort_by = (sort_by or "admissionDate").strip()
        reverse = (sort_dir or "desc").strip().lower() != "asc"
        key_map = {
            "admissionDate": lambda student: (student.admission_date is None, student.admission_date),
            "createdAt": lambda student: (student.created_at is None, student.created_at),
            "firstName": lambda student: (student.first_name or "").lower(),
            "lastName": lambda student: (student.last_name or "").lower(),
            "studentCode": lambda student: (student.student_code or "").lower(),
        }
        return sorted(students, key=key_map.get(normalized_sort_by, key_map["admissionDate"]), reverse=reverse)

    def to_read(self, student: Student) -> StudentRead:
        return StudentRead(
            student_id=student.student_id,
            student_code=student.student_code,
            first_name=student.first_name,
            last_name=student.last_name,
            dob=student.dob,
            gender=student.gender,
            phone_number=student.phone_number,
            email=student.email,
            course_code=student.course_code,
            admission_date=student.admission_date,
            address=student.address,
            guardian_name=student.guardian_name,
            guardian_contact=student.guardian_contact,
            blood_group=student.blood_group,
            created_at=student.created_at,
        )

