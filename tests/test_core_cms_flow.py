from __future__ import annotations

from datetime import date
from decimal import Decimal
import os
import unittest

from fastapi import HTTPException

from app.core.config import clear_settings_cache
from app.db.session import initialize_database, reset_database_state, session_context
from app.modules.admissions.schemas import AdmissionWriteRequest
from app.modules.admissions.service import AdmissionService
from app.modules.attendance.repository import AttendanceRepository
from app.modules.attendance.schemas import AttendanceWriteRequest
from app.modules.attendance.service import AttendanceService
from app.modules.auth.authorization import AuthorizationService
from app.modules.auth.jwt import JwtService
from app.modules.auth.refresh_token_repository import RefreshTokenRepository
from app.modules.auth.schemas import LoginRequest, LogoutRequest, RefreshRequest, StudentRegistrationRequest
from app.modules.auth.service import AuthService
from app.modules.courses.repository import CourseRepository
from app.modules.courses.schemas import CourseWriteRequest
from app.modules.courses.service import CourseService
from app.modules.dashboard.service import DashboardService
from app.modules.fees.repository import FeeRepository
from app.modules.fees.schemas import FeeWriteRequest
from app.modules.fees.service import FeeService
from app.modules.marks.repository import StudentMarkRepository
from app.modules.marks.schemas import StudentMarkWriteRequest
from app.modules.marks.service import StudentMarkService
from app.modules.reports.service import ReportService
from app.modules.staff.repository import StaffRepository
from app.modules.staff.schemas import StaffWriteRequest
from app.modules.staff.service import StaffService
from app.modules.students.repository import StudentRepository
from app.modules.students.service import StudentService
from app.modules.subjects.repository import SubjectRepository
from app.modules.subjects.schemas import SubjectWriteRequest
from app.modules.subjects.service import SubjectService
from app.modules.teachers.repository import TeacherCourseRepository, TeacherRepository, TeacherSubjectRepository
from app.modules.teachers.schemas import TeacherWriteRequest
from app.modules.teachers.service import TeacherService
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserMutationRequest
from app.modules.users.service import UserService


class CoreCmsFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_env = os.environ.copy()
        os.environ.update(
            {
                "APP_ENV": "test",
                "DB_URL": "sqlite+pysqlite:///:memory:",
                "DOCS_ENABLED": "false",
                "JWT_SECRET": "test-secret-value-for-college-server",
                "JWT_ISSUER": "college-server",
                "JWT_AUDIENCE": "college-clients",
                "TRUSTED_HOSTS": "testserver,localhost,127.0.0.1",
            }
        )
        clear_settings_cache()
        reset_database_state()
        initialize_database()

    def tearDown(self) -> None:
        reset_database_state()
        clear_settings_cache()
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_complete_college_server_flow(self) -> None:
        with session_context() as session:
            context = self.seed_college(session)
            auth_service = context["auth_service"]
            users = context["users"]

            login = auth_service.login(LoginRequest(login_id="admin", password="admin12345"))
            refreshed = auth_service.refresh(RefreshRequest(refresh_token=login.refresh_token))
            self.assertTrue(refreshed.access_token)
            auth_service.logout(LogoutRequest(refresh_token=refreshed.refresh_token))

            dashboard = context["dashboard_service"].get_summary()
            self.assertEqual(dashboard.total_students, 1)
            self.assertEqual(dashboard.total_teachers, 1)
            self.assertEqual(dashboard.total_staff, 1)
            self.assertEqual(dashboard.pending_fee_count, 1)
            self.assertEqual(dashboard.pending_fee_amount, Decimal("12000.00"))

            student_report = context["report_service"].get_student_report(context["student_id"])
            self.assertEqual(student_report.present_days, 1)
            self.assertEqual(student_report.pending_fees_amount, Decimal("12000.00"))
            self.assertEqual(len(student_report.marks), 1)

            teacher_report = context["report_service"].get_teacher_report(context["teacher_id"])
            self.assertEqual(len(teacher_report.courses), 1)
            self.assertEqual(len(teacher_report.subjects), 1)

            teacher_user = users.find_by_id(context["teacher_user_id"])
            student = context["student_repository"].find_by_id(context["student_id"])
            subject = context["subject_repository"].find_by_id(context["subject_id"])
            self.assertIsNotNone(teacher_user)
            self.assertIsNotNone(student)
            self.assertIsNotNone(subject)
            authz = AuthorizationService(session)
            self.assertTrue(authz.can_access_student(teacher_user, student))
            self.assertTrue(authz.can_access_subject(teacher_user, subject))

    def test_user_profile_links_must_exist(self) -> None:
        with session_context() as session:
            user_service = UserService(UserRepository(session))
            with self.assertRaises(HTTPException) as raised:
                user_service.create_user(
                    UserMutationRequest(
                        login_id="STU-404",
                        password="student12345",
                        email="missing@example.com",
                        role="Student",
                        student_id=404,
                    )
                )
            self.assertEqual(raised.exception.status_code, 404)

    def test_student_can_self_register_after_admin_enters_admission(self) -> None:
        with session_context() as session:
            users = UserRepository(session)
            auth_service = AuthService(users, RefreshTokenRepository(session), JwtService())
            course_repository = CourseRepository(session)
            student_repository = StudentRepository(session)
            course_service = CourseService(course_repository)
            student_service = StudentService(student_repository, course_repository)
            admission_service = AdmissionService(student_service)

            course_service.create_course(CourseWriteRequest(course_code="BSC101", course_name="BSc"))
            admission = admission_service.create_admission(
                AdmissionWriteRequest(
                    first_name="Asha",
                    last_name="Rawat",
                    dob=date(2005, 1, 10),
                    gender="Female",
                    phone_number="9191919191",
                    email="asha@example.com",
                    course_code="BSC101",
                    admission_date=date(2024, 7, 1),
                )
            )
            student = student_repository.find_by_id(admission.student_id)
            self.assertIsNotNone(student)
            assert student is not None

            with self.assertRaises(HTTPException) as mismatch:
                auth_service.register_student(
                    StudentRegistrationRequest(
                        student_id=admission.student_id,
                        email="asha@example.com",
                        dob=date(2005, 1, 11),
                        password="student12345",
                    )
                )
            self.assertEqual(mismatch.exception.status_code, 400)

            registration = auth_service.register_student(
                StudentRegistrationRequest(
                    student_id=admission.student_id,
                    email="asha@example.com",
                    dob=date(2005, 1, 10),
                    password="student12345",
                )
            )
            self.assertEqual(registration.role, "Student")
            self.assertEqual(registration.student_id, admission.student_id)
            self.assertEqual(registration.login_id, student.student_code)
            self.assertTrue(registration.access_token)

            login = auth_service.login(LoginRequest(login_id=student.student_code, password="student12345"))
            self.assertEqual(login.student_id, admission.student_id)

            with self.assertRaises(HTTPException) as duplicate:
                auth_service.register_student(
                    StudentRegistrationRequest(
                        student_code=student.student_code,
                        email="asha@example.com",
                        dob=date(2005, 1, 10),
                        password="student12345",
                    )
                )
            self.assertEqual(duplicate.exception.status_code, 400)

    def seed_college(self, session):
        users = UserRepository(session)
        user_service = UserService(users)
        auth_service = AuthService(users, RefreshTokenRepository(session), JwtService())

        course_repository = CourseRepository(session)
        subject_repository = SubjectRepository(session)
        student_repository = StudentRepository(session)
        teacher_repository = TeacherRepository(session)
        staff_repository = StaffRepository(session)
        attendance_repository = AttendanceRepository(session)
        fee_repository = FeeRepository(session)
        mark_repository = StudentMarkRepository(session)
        teacher_course_repository = TeacherCourseRepository(session)
        teacher_subject_repository = TeacherSubjectRepository(session)

        course_service = CourseService(course_repository)
        subject_service = SubjectService(subject_repository, course_repository)
        student_service = StudentService(student_repository, course_repository)
        teacher_service = TeacherService(
            teacher_repository,
            course_repository,
            subject_repository,
            teacher_course_repository,
            teacher_subject_repository,
        )
        staff_service = StaffService(staff_repository)
        attendance_service = AttendanceService(attendance_repository, student_repository)
        fee_service = FeeService(fee_repository, student_repository)
        mark_service = StudentMarkService(mark_repository, student_repository, subject_repository)
        admission_service = AdmissionService(student_service)

        user_service.create_user(UserMutationRequest(login_id="admin", password="admin12345", email="admin@example.com", role="Admin"))
        course_service.create_course(CourseWriteRequest(course_code="BCA101", course_name="BCA"))
        subject = subject_service.create_subject(
            SubjectWriteRequest(subject_code="CS101", subject_name="Programming", course_code="BCA101")
        )
        admission = admission_service.create_admission(
            AdmissionWriteRequest(
                first_name="Rohit",
                last_name="Verma",
                dob=date(2004, 8, 22),
                gender="Male",
                phone_number="9898989898",
                email="rohit@example.com",
                course_code="BCA101",
                admission_date=date(2022, 7, 1),
            )
        )
        staff = staff_service.create_staff(
            StaffWriteRequest(
                staff_code="STF-00001",
                first_name="Kiran",
                last_name="Patel",
                dob=date(1990, 2, 14),
                gender="Male",
                phone_number="9494949494",
                email="kiran@example.com",
                hire_date=date(2021, 5, 3),
                role="Administration",
            )
        )
        teacher = teacher_service.create_teacher(
            TeacherWriteRequest(
                teacher_code="TCH-00001",
                first_name="Suman",
                last_name="Mehta",
                dob=date(1988, 4, 12),
                gender="Female",
                phone_number="9696969696",
                email="suman@example.com",
                hire_date=date(2020, 6, 1),
                course_codes=["BCA101"],
                subject_ids=[subject.subject_id],
            )
        )
        user_service.create_user(
            UserMutationRequest(
                login_id="STU-00001",
                password="student12345",
                email="student-login@example.com",
                role="Student",
                student_id=admission.student_id,
            )
        )
        teacher_user = user_service.create_user(
            UserMutationRequest(
                login_id="TCH-00001",
                password="teacher12345",
                email="teacher-login@example.com",
                role="Teacher",
                teacher_id=teacher.teacher_id,
            )
        )
        user_service.create_user(
            UserMutationRequest(
                login_id="STF-00001",
                password="staff12345",
                email="staff-login@example.com",
                role="Staff",
                staff_id=staff.staff_id,
            )
        )

        attendance_service.create_attendance(
            AttendanceWriteRequest(student_id=admission.student_id, date=date(2026, 5, 27), status="Present")
        )
        fee_service.create_fee(
            FeeWriteRequest(student_id=admission.student_id, amount=Decimal("12000.00"), status="Pending", due_date=date(2026, 6, 15))
        )
        mark_service.create_mark(
            StudentMarkWriteRequest(
                student_id=admission.student_id,
                subject_id=subject.subject_id,
                semester=1,
                exam_type="Midterm",
                marks_obtained=Decimal("82.50"),
                max_marks=Decimal("100.00"),
                grade="A",
                exam_date=date(2026, 5, 20),
            )
        )

        dashboard_service = DashboardService(
            student_repository,
            teacher_repository,
            staff_repository,
            course_repository,
            subject_repository,
            users,
            attendance_repository,
            fee_repository,
            mark_repository,
            teacher_course_repository,
            teacher_subject_repository,
            admission_service,
        )
        report_service = ReportService(
            student_service,
            teacher_service,
            attendance_service,
            fee_service,
            mark_service,
            course_service,
            subject_service,
        )
        return {
            "auth_service": auth_service,
            "users": users,
            "student_repository": student_repository,
            "subject_repository": subject_repository,
            "dashboard_service": dashboard_service,
            "report_service": report_service,
            "student_id": admission.student_id,
            "teacher_id": teacher.teacher_id,
            "subject_id": subject.subject_id,
            "teacher_user_id": teacher_user.user_id,
        }


if __name__ == "__main__":
    unittest.main()
