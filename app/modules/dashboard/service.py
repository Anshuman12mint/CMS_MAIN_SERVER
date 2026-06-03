from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel

from app.modules.admissions.service import AdmissionService
from app.modules.attendance.repository import AttendanceRepository
from app.modules.attendance.service import AttendanceService
from app.modules.courses.repository import CourseRepository
from app.modules.courses.service import CourseService
from app.modules.dashboard.schemas import DashboardSummary, UserDashboard
from app.modules.fees.repository import FeeRepository
from app.modules.fees.service import FeeService
from app.modules.marks.repository import StudentMarkRepository
from app.modules.marks.service import StudentMarkService
from app.modules.staff.repository import StaffRepository
from app.modules.staff.service import StaffService
from app.modules.students.repository import StudentRepository
from app.modules.students.service import StudentService
from app.modules.subjects.repository import SubjectRepository
from app.modules.subjects.service import SubjectService
from app.modules.teachers.repository import TeacherCourseRepository, TeacherRepository, TeacherSubjectRepository
from app.modules.teachers.service import TeacherService
from app.modules.users.model import User
from app.modules.users.repository import UserRepository


class DashboardService:
    def __init__(
        self,
        student_repository: StudentRepository,
        teacher_repository: TeacherRepository,
        staff_repository: StaffRepository,
        course_repository: CourseRepository,
        subject_repository: SubjectRepository,
        user_repository: UserRepository,
        attendance_repository: AttendanceRepository,
        fee_repository: FeeRepository,
        student_mark_repository: StudentMarkRepository,
        teacher_course_repository: TeacherCourseRepository,
        teacher_subject_repository: TeacherSubjectRepository,
        admission_service: AdmissionService,
    ) -> None:
        self.student_repository = student_repository
        self.teacher_repository = teacher_repository
        self.staff_repository = staff_repository
        self.course_repository = course_repository
        self.subject_repository = subject_repository
        self.user_repository = user_repository
        self.attendance_repository = attendance_repository
        self.fee_repository = fee_repository
        self.student_mark_repository = student_mark_repository
        self.teacher_course_repository = teacher_course_repository
        self.teacher_subject_repository = teacher_subject_repository
        self.admission_service = admission_service

    def get_summary(self) -> DashboardSummary:
        recent_admissions = self.admission_service.get_admissions()[:5]
        return DashboardSummary(
            total_students=self.student_repository.count(),
            total_teachers=self.teacher_repository.count(),
            total_staff=self.staff_repository.count(),
            total_courses=self.course_repository.count(),
            total_subjects=self.subject_repository.count(),
            total_users=self.user_repository.count(),
            total_admissions=len(self.admission_service.get_admissions()),
            total_attendance_records=self.attendance_repository.count(),
            total_marks_recorded=self.student_mark_repository.count(),
            pending_fee_count=self.fee_repository.count_by_status("Pending"),
            pending_fee_amount=self.fee_repository.sum_pending_amount() or Decimal("0"),
            recent_admissions=recent_admissions,
        )

    def get_dashboard_for_user(self, user: User) -> UserDashboard:
        role = (user.role or "").strip().lower()
        if role == "student":
            return self.get_student_dashboard(user)
        if role == "teacher":
            return self.get_teacher_dashboard(user)
        if role == "staff":
            return self.get_staff_dashboard(user)
        if role == "admin":
            return UserDashboard(type="admin", summary=self.dump(self.get_summary()))
        return UserDashboard(type="basic", summary=self.dump(self.get_summary()))

    def get_staff_dashboard(self, user: User) -> UserDashboard:
        staff = self.staff_repository.find_by_id(user.staff_id)
        profile = StaffService(self.staff_repository).to_read(staff) if staff is not None else None
        return UserDashboard(type="staff", profile=self.dump(profile), summary=self.dump(self.get_summary()))

    def get_student_dashboard(self, user: User) -> UserDashboard:
        student = self.student_repository.find_by_id(user.student_id)
        if student is None:
            return UserDashboard(type="student", message="No student profile is linked to this user.")

        student_service = StudentService(self.student_repository, self.course_repository)
        attendance_service = AttendanceService(self.attendance_repository, self.student_repository)
        fee_service = FeeService(self.fee_repository, self.student_repository)
        mark_service = StudentMarkService(self.student_mark_repository, self.student_repository, self.subject_repository)

        attendance = attendance_service.get_attendance(student.student_id)
        fees = fee_service.get_fees(student.student_id)
        marks = mark_service.get_marks(student.student_id)
        pending_fees = [fee for fee in fees if self.matches_status(fee.status, "Pending")]

        return UserDashboard(
            type="student",
            profile=self.dump(student_service.to_read(student)),
            quick_stats={
                "presentDays": sum(1 for item in attendance if self.matches_status(item.status, "Present")),
                "absentDays": sum(1 for item in attendance if self.matches_status(item.status, "Absent")),
                "totalAttendanceRecords": len(attendance),
                "totalFees": self.sum_fees(fees),
                "paidFees": self.sum_fees([fee for fee in fees if self.matches_status(fee.status, "Paid")]),
                "pendingFeeCount": len(pending_fees),
                "pendingFeesAmount": self.sum_fees(pending_fees),
                "marksRecorded": len(marks),
            },
            recent_attendance=self.dump(attendance[:5]),
            recent_fees=self.dump(fees[:5]),
            pending_fees=self.dump(pending_fees[:5]),
            recent_marks=self.dump(marks[:5]),
        )

    def get_teacher_dashboard(self, user: User) -> UserDashboard:
        teacher = self.teacher_repository.find_by_id(user.teacher_id)
        if teacher is None:
            return UserDashboard(type="teacher", message="No teacher profile is linked to this user.")

        teacher_service = self.create_teacher_service()
        course_service = CourseService(self.course_repository)
        subject_service = SubjectService(self.subject_repository, self.course_repository)
        teacher_read = teacher_service.to_read(teacher)
        courses = [course_service.get_course(course_code) for course_code in teacher_read.course_codes]
        subjects = [subject_service.get_subject(subject_id) for subject_id in teacher_read.subject_ids]
        students_by_course = {
            course_code: len(self.student_repository.find_by_course_code_ordered(course_code))
            for course_code in teacher_read.course_codes
        }

        return UserDashboard(
            type="teacher",
            profile=self.dump(teacher_read),
            quick_stats={
                "assignedCourses": len(teacher_read.course_codes),
                "assignedSubjects": len(teacher_read.subject_ids),
                "studentsInAssignedCourses": sum(students_by_course.values()),
            },
            courses=self.dump(courses),
            subjects=self.dump(subjects),
            students_by_course=students_by_course,
        )

    def create_teacher_service(self) -> TeacherService:
        return TeacherService(
            self.teacher_repository,
            self.course_repository,
            self.subject_repository,
            self.teacher_course_repository,
            self.teacher_subject_repository,
        )

    def matches_status(self, value: str | None, expected: str) -> bool:
        return (value or "").strip().lower() == expected.lower()

    def sum_fees(self, fees) -> Decimal:
        total = Decimal("0")
        for fee in fees:
            if fee.amount is not None:
                total += fee.amount
        return total

    def dump(self, value):
        if isinstance(value, BaseModel):
            return value.model_dump(mode="json", by_alias=True)
        if isinstance(value, list):
            return [self.dump(item) for item in value]
        if isinstance(value, dict):
            return {key: self.dump(item) for key, item in value.items()}
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, date | datetime):
            return value.isoformat()
        return value

