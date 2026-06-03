from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.staff.model import Staff
from app.modules.staff.repository import StaffRepository
from app.modules.students.model import Student
from app.modules.students.repository import StudentRepository
from app.modules.subjects.model import Subject
from app.modules.subjects.repository import SubjectRepository
from app.modules.teachers.model import Teacher
from app.modules.teachers.repository import TeacherCourseRepository, TeacherRepository, TeacherSubjectRepository
from app.modules.users.model import User


class AuthorizationService:
    def __init__(self, session: Session) -> None:
        self.student_repository = StudentRepository(session)
        self.teacher_repository = TeacherRepository(session)
        self.staff_repository = StaffRepository(session)
        self.subject_repository = SubjectRepository(session)
        self.teacher_course_repository = TeacherCourseRepository(session)
        self.teacher_subject_repository = TeacherSubjectRepository(session)

    def role_of(self, current_user: User) -> str:
        return (current_user.role or "").strip().lower()

    def is_admin(self, current_user: User) -> bool:
        return self.role_of(current_user) == "admin"

    def is_staff(self, current_user: User) -> bool:
        return self.role_of(current_user) == "staff"

    def is_teacher(self, current_user: User) -> bool:
        return self.role_of(current_user) == "teacher"

    def is_student(self, current_user: User) -> bool:
        return self.role_of(current_user) == "student"

    def is_admin_or_staff(self, current_user: User) -> bool:
        return self.is_admin(current_user) or self.is_staff(current_user)

    def ensure_admin_or_staff(self, current_user: User, detail: str = "Access is denied") -> None:
        if not self.is_admin_or_staff(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    def resolve_current_student(self, current_user: User) -> Student | None:
        return self.student_repository.find_by_id(current_user.student_id)

    def require_current_student(self, current_user: User) -> Student:
        student = self.resolve_current_student(current_user)
        if student is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student profile is not linked to this account")
        return student

    def resolve_current_teacher(self, current_user: User) -> Teacher | None:
        return self.teacher_repository.find_by_id(current_user.teacher_id)

    def require_current_teacher(self, current_user: User) -> Teacher:
        teacher = self.resolve_current_teacher(current_user)
        if teacher is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Teacher profile is not linked to this account")
        return teacher

    def resolve_current_staff(self, current_user: User) -> Staff | None:
        return self.staff_repository.find_by_id(current_user.staff_id)

    def require_current_staff(self, current_user: User) -> Staff:
        staff = self.resolve_current_staff(current_user)
        if staff is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Staff profile is not linked to this account")
        return staff

    def get_teacher_course_codes(self, current_user: User) -> set[str]:
        teacher = self.resolve_current_teacher(current_user)
        if teacher is None:
            return set()

        course_codes = {assignment.course_code for assignment in self.teacher_course_repository.find_by_teacher_id(teacher.teacher_id)}
        for assignment in self.teacher_subject_repository.find_by_teacher_id(teacher.teacher_id):
            subject = self.subject_repository.find_by_id(assignment.subject_id)
            if subject is not None and subject.course_code:
                course_codes.add(subject.course_code)
        return {course_code for course_code in course_codes if course_code}

    def get_teacher_subject_ids(self, current_user: User) -> set[int]:
        teacher = self.resolve_current_teacher(current_user)
        if teacher is None:
            return set()
        return {assignment.subject_id for assignment in self.teacher_subject_repository.find_by_teacher_id(teacher.teacher_id)}

    def can_access_course(self, current_user: User, course_code: str | None) -> bool:
        if self.is_admin_or_staff(current_user):
            return True
        if course_code is None:
            return False
        if self.is_teacher(current_user):
            return course_code in self.get_teacher_course_codes(current_user)
        if self.is_student(current_user):
            return self.require_current_student(current_user).course_code == course_code
        return False

    def can_access_student(self, current_user: User, student: Student) -> bool:
        if self.is_admin_or_staff(current_user):
            return True
        if self.is_student(current_user):
            return self.require_current_student(current_user).student_id == student.student_id
        if self.is_teacher(current_user):
            return self.can_access_course(current_user, student.course_code)
        return False

    def ensure_student_access(self, current_user: User, student: Student, detail: str = "Access is denied") -> None:
        if not self.can_access_student(current_user, student):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    def can_access_fee_student(self, current_user: User, student: Student) -> bool:
        if self.is_admin_or_staff(current_user):
            return True
        if self.is_student(current_user):
            return self.require_current_student(current_user).student_id == student.student_id
        return False

    def ensure_fee_student_access(self, current_user: User, student: Student, detail: str = "Access is denied") -> None:
        if not self.can_access_fee_student(current_user, student):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    def ensure_attendance_mutation_access(self, current_user: User, student: Student) -> None:
        if self.is_admin_or_staff(current_user):
            return
        if self.is_teacher(current_user) and self.can_access_course(current_user, student.course_code):
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff, admins, or assigned teachers can manage attendance",
        )

    def can_access_teacher(self, current_user: User, teacher: Teacher) -> bool:
        if self.is_admin_or_staff(current_user):
            return True
        if self.is_teacher(current_user):
            current_teacher = self.require_current_teacher(current_user)
            return current_teacher.teacher_id == teacher.teacher_id
        return False

    def ensure_teacher_access(self, current_user: User, teacher: Teacher, detail: str = "Access is denied") -> None:
        if not self.can_access_teacher(current_user, teacher):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    def can_access_subject(self, current_user: User, subject: Subject) -> bool:
        if self.is_admin_or_staff(current_user):
            return True
        if self.is_teacher(current_user):
            assigned_subjects = self.get_teacher_subject_ids(current_user)
            return subject.subject_id in assigned_subjects or self.can_access_course(current_user, subject.course_code)
        if self.is_student(current_user):
            return self.require_current_student(current_user).course_code == subject.course_code
        return False

    def ensure_subject_access(self, current_user: User, subject: Subject, detail: str = "Access is denied") -> None:
        if not self.can_access_subject(current_user, subject):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    def ensure_mark_mutation_access(self, current_user: User, student: Student, subject: Subject) -> None:
        if self.is_admin_or_staff(current_user):
            return
        if self.is_teacher(current_user):
            if not self.can_access_course(current_user, student.course_code):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Teacher is not assigned to this student's course")
            assigned_subjects = self.get_teacher_subject_ids(current_user)
            if assigned_subjects and subject.subject_id not in assigned_subjects:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Teacher is not assigned to this subject")
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff, admins, or assigned teachers can manage marks",
        )
