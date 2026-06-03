from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import utc_now
from app.core.security import hash_password
from app.db.session import session_context
from app.modules.attendance.model import Attendance
from app.modules.courses.model import Course
from app.modules.fees.model import Fee
from app.modules.marks.model import StudentMark
from app.modules.staff.model import Staff
from app.modules.students.model import Student
from app.modules.subjects.model import Subject
from app.modules.teachers.model import Teacher, TeacherCourse, TeacherSubject
from app.modules.users.model import User


DEMO_PASSWORD = "demo12345"


def main() -> None:
    with session_context() as session:
        courses = seed_courses(session)
        subjects = seed_subjects(session)
        teachers = seed_teachers(session)
        staff_members = seed_staff(session)
        students = seed_students(session)
        seed_teacher_assignments(session, teachers, courses, subjects)
        seed_users(session, teachers, staff_members, students)
        seed_attendance(session, students)
        seed_fees(session, students)
        seed_marks(session, students, subjects)
        session.flush()

        print("Demo data seeded.")
        print("")
        print("Demo logins:")
        print("  ADMIN / admin12345")
        print("  TCH-0001 / demo12345")
        print("  STF-0001 / demo12345")
        print("  STU-0001 / demo12345")
        print("  STU-0002 / demo12345")
        print("")
        print("Student registration demo record:")
        print("  studentCode: STU-0003")
        print("  email: kabir.khan.demo@college.local")
        print("  dob: 2005-12-02")


def seed_courses(session) -> dict[str, Course]:
    rows = [
        ("BCA", "Bachelor of Computer Applications", "Computer science, programming, databases, and web systems."),
        ("BBA", "Bachelor of Business Administration", "Management, finance, marketing, and business communication."),
        ("MBA", "Master of Business Administration", "Postgraduate management, analytics, and leadership program."),
    ]
    return {
        code: upsert_by_pk(
            session,
            Course,
            code,
            "course_code",
            course_code=code,
            course_name=name,
            course_description=description,
        )
        for code, name, description in rows
    }


def seed_subjects(session) -> dict[str, Subject]:
    rows = [
        ("BCA101", "Programming Fundamentals", "BCA", "Python, algorithms, and problem solving."),
        ("BCA102", "Database Management Systems", "BCA", "Relational design, SQL, and transactions."),
        ("BCA103", "Web Technologies", "BCA", "HTML, CSS, JavaScript, and API integration."),
        ("BBA101", "Principles of Management", "BBA", "Management foundations and organization design."),
        ("BBA102", "Business Communication", "BBA", "Professional writing, speaking, and presentation skills."),
        ("MBA101", "Organizational Behaviour", "MBA", "Teams, leadership, motivation, and workplace culture."),
    ]
    subjects: dict[str, Subject] = {}
    for code, name, course_code, description in rows:
        subject = session.query(Subject).filter(Subject.subject_code == code).one_or_none()
        if subject is None:
            subject = Subject(subject_code=code)
            session.add(subject)
        subject.subject_name = name
        subject.course_code = course_code
        subject.subject_description = description
        session.flush()
        subjects[code] = subject
    return subjects


def seed_teachers(session) -> dict[str, Teacher]:
    rows = [
        {
            "teacher_code": "TCH-0001",
            "first_name": "Meera",
            "last_name": "Sharma",
            "dob": date(1988, 3, 14),
            "gender": "Female",
            "phone_number": "9000001001",
            "email": "meera.sharma.demo@college.local",
            "hire_date": date(2018, 7, 1),
            "department": "Computer Applications",
            "address": "Dehradun, Uttarakhand",
            "qualification": "MCA",
            "salary": Decimal("62000.00"),
        },
        {
            "teacher_code": "TCH-0002",
            "first_name": "Arvind",
            "last_name": "Rao",
            "dob": date(1982, 11, 22),
            "gender": "Male",
            "phone_number": "9000001002",
            "email": "arvind.rao.demo@college.local",
            "hire_date": date(2016, 8, 12),
            "department": "Management",
            "address": "Rishikesh, Uttarakhand",
            "qualification": "MBA, PhD",
            "salary": Decimal("78000.00"),
        },
    ]
    return {row["teacher_code"]: upsert_by_code(session, Teacher, "teacher_code", row) for row in rows}


def seed_staff(session) -> dict[str, Staff]:
    rows = [
        {
            "staff_code": "STF-0001",
            "first_name": "Nisha",
            "last_name": "Verma",
            "dob": date(1990, 9, 5),
            "gender": "Female",
            "phone_number": "9000002001",
            "email": "nisha.verma.demo@college.local",
            "hire_date": date(2020, 1, 10),
            "role": "Administration",
            "department": "Admissions",
            "address": "Dehradun, Uttarakhand",
            "salary": Decimal("36000.00"),
        },
        {
            "staff_code": "STF-0002",
            "first_name": "Rohan",
            "last_name": "Singh",
            "dob": date(1986, 6, 18),
            "gender": "Male",
            "phone_number": "9000002002",
            "email": "rohan.singh.demo@college.local",
            "hire_date": date(2019, 4, 15),
            "role": "Librarian",
            "department": "Library",
            "address": "Haridwar, Uttarakhand",
            "salary": Decimal("34000.00"),
        },
    ]
    return {row["staff_code"]: upsert_by_code(session, Staff, "staff_code", row) for row in rows}


def seed_students(session) -> dict[str, Student]:
    rows = [
        {
            "student_code": "STU-0001",
            "first_name": "Aarav",
            "last_name": "Mehta",
            "dob": date(2005, 4, 12),
            "gender": "Male",
            "phone_number": "9000003001",
            "email": "aarav.mehta.demo@college.local",
            "course_code": "BCA",
            "admission_date": date(2024, 7, 15),
            "address": "Mussoorie Road, Dehradun",
            "guardian_name": "Rakesh Mehta",
            "guardian_contact": "9100003001",
            "blood_group": "B+",
        },
        {
            "student_code": "STU-0002",
            "first_name": "Priya",
            "last_name": "Nair",
            "dob": date(2005, 8, 20),
            "gender": "Female",
            "phone_number": "9000003002",
            "email": "priya.nair.demo@college.local",
            "course_code": "BBA",
            "admission_date": date(2024, 7, 16),
            "address": "Rajpur Road, Dehradun",
            "guardian_name": "Sanjay Nair",
            "guardian_contact": "9100003002",
            "blood_group": "O+",
        },
        {
            "student_code": "STU-0003",
            "first_name": "Kabir",
            "last_name": "Khan",
            "dob": date(2005, 12, 2),
            "gender": "Male",
            "phone_number": "9000003003",
            "email": "kabir.khan.demo@college.local",
            "course_code": "BCA",
            "admission_date": date(2024, 7, 18),
            "address": "Prem Nagar, Dehradun",
            "guardian_name": "Farah Khan",
            "guardian_contact": "9100003003",
            "blood_group": "A+",
        },
    ]
    return {row["student_code"]: upsert_by_code(session, Student, "student_code", row) for row in rows}


def seed_teacher_assignments(session, teachers, courses, subjects) -> None:
    _ = courses
    assignments = {
        "TCH-0001": {"courses": ["BCA"], "subjects": ["BCA101", "BCA102", "BCA103"]},
        "TCH-0002": {"courses": ["BBA", "MBA"], "subjects": ["BBA101", "BBA102", "MBA101"]},
    }
    for teacher_code, values in assignments.items():
        teacher = teachers[teacher_code]
        for course_code in values["courses"]:
            exists = session.get(TeacherCourse, {"teacher_id": teacher.teacher_id, "course_code": course_code})
            if exists is None:
                session.add(TeacherCourse(teacher_id=teacher.teacher_id, course_code=course_code))
        for subject_code in values["subjects"]:
            subject = subjects[subject_code]
            exists = session.get(TeacherSubject, {"teacher_id": teacher.teacher_id, "subject_id": subject.subject_id})
            if exists is None:
                session.add(TeacherSubject(teacher_id=teacher.teacher_id, subject_id=subject.subject_id))


def seed_users(session, teachers, staff_members, students) -> None:
    ensure_user(
        session,
        login_id="TCH-0001",
        email="meera.sharma.login@college.local",
        role="Teacher",
        profile_field="teacher_id",
        profile_id=teachers["TCH-0001"].teacher_id,
    )
    ensure_user(
        session,
        login_id="STF-0001",
        email="nisha.verma.login@college.local",
        role="Staff",
        profile_field="staff_id",
        profile_id=staff_members["STF-0001"].staff_id,
    )
    ensure_user(
        session,
        login_id="STU-0001",
        email="aarav.mehta.login@college.local",
        role="Student",
        profile_field="student_id",
        profile_id=students["STU-0001"].student_id,
    )
    ensure_user(
        session,
        login_id="STU-0002",
        email="priya.nair.login@college.local",
        role="Student",
        profile_field="student_id",
        profile_id=students["STU-0002"].student_id,
    )


def seed_attendance(session, students) -> None:
    statuses = {
        "STU-0001": ["Present", "Present", "Absent", "Present", "Present"],
        "STU-0002": ["Present", "Absent", "Present", "Present", "Present"],
        "STU-0003": ["Present", "Present", "Present", "Absent", "Present"],
    }
    days = [date(2026, 5, 18), date(2026, 5, 19), date(2026, 5, 20), date(2026, 5, 21), date(2026, 5, 22)]
    for student_code, values in statuses.items():
        student = students[student_code]
        for day, status in zip(days, values, strict=True):
            attendance = (
                session.query(Attendance)
                .filter(Attendance.student_id == student.student_id, Attendance.date == day)
                .one_or_none()
            )
            if attendance is None:
                attendance = Attendance(student_id=student.student_id, date=day)
                session.add(attendance)
            attendance.status = status


def seed_fees(session, students) -> None:
    rows = [
        ("STU-0001", Decimal("28000.00"), "Paid", date(2026, 4, 30)),
        ("STU-0001", Decimal("28000.00"), "Pending", date(2026, 6, 30)),
        ("STU-0002", Decimal("26000.00"), "Paid", date(2026, 4, 30)),
        ("STU-0002", Decimal("26000.00"), "Pending", date(2026, 6, 30)),
        ("STU-0003", Decimal("28000.00"), "Pending", date(2026, 6, 30)),
    ]
    for student_code, amount, status, due_date in rows:
        student = students[student_code]
        fee = (
            session.query(Fee)
            .filter(Fee.student_id == student.student_id, Fee.due_date == due_date, Fee.amount == amount)
            .one_or_none()
        )
        if fee is None:
            fee = Fee(student_id=student.student_id, amount=amount, due_date=due_date)
            session.add(fee)
        fee.status = status


def seed_marks(session, students, subjects) -> None:
    rows = [
        ("STU-0001", "BCA101", 2, "Midterm", Decimal("43.00"), Decimal("50.00"), "A", date(2026, 5, 6)),
        ("STU-0001", "BCA102", 2, "Midterm", Decimal("39.00"), Decimal("50.00"), "B", date(2026, 5, 8)),
        ("STU-0001", "BCA103", 2, "Assignment", Decimal("18.00"), Decimal("20.00"), "A", date(2026, 5, 10)),
        ("STU-0002", "BBA101", 2, "Midterm", Decimal("41.00"), Decimal("50.00"), "A", date(2026, 5, 7)),
        ("STU-0002", "BBA102", 2, "Assignment", Decimal("17.00"), Decimal("20.00"), "A", date(2026, 5, 11)),
        ("STU-0003", "BCA101", 2, "Midterm", Decimal("36.00"), Decimal("50.00"), "B", date(2026, 5, 6)),
        ("STU-0003", "BCA102", 2, "Practical", Decimal("44.00"), Decimal("50.00"), "A", date(2026, 5, 13)),
    ]
    for student_code, subject_code, semester, exam_type, marks, max_marks, grade, exam_date in rows:
        student = students[student_code]
        subject = subjects[subject_code]
        mark = (
            session.query(StudentMark)
            .filter(
                StudentMark.student_id == student.student_id,
                StudentMark.subject_id == subject.subject_id,
                StudentMark.semester == semester,
                StudentMark.exam_type == exam_type,
            )
            .one_or_none()
        )
        if mark is None:
            mark = StudentMark(
                student_id=student.student_id,
                subject_id=subject.subject_id,
                semester=semester,
                exam_type=exam_type,
            )
            session.add(mark)
        mark.marks_obtained = marks
        mark.max_marks = max_marks
        mark.grade = grade
        mark.exam_date = exam_date


def ensure_user(session, login_id: str, email: str, role: str, profile_field: str, profile_id: int) -> User:
    user = session.query(User).filter(User.login_id == login_id).one_or_none()
    if user is None:
        user = User(login_id=login_id, legacy_username=login_id, registered_at=utc_now())
        session.add(user)
    user.email = email
    user.password_hash = hash_password(DEMO_PASSWORD)
    user.role = role
    user.account_status = "ACTIVE"
    user.student_id = None
    user.teacher_id = None
    user.staff_id = None
    setattr(user, profile_field, profile_id)
    return user


def upsert_by_pk(session, model, pk_value, pk_field: str, **values):
    obj = session.get(model, pk_value)
    if obj is None:
        obj = model()
        session.add(obj)
    for key, value in values.items():
        setattr(obj, key, value)
    session.flush()
    return obj


def upsert_by_code(session, model, code_field: str, values: dict):
    code = values[code_field]
    obj = session.query(model).filter(getattr(model, code_field) == code).one_or_none()
    if obj is None:
        obj = model()
        session.add(obj)
    for key, value in values.items():
        setattr(obj, key, value)
    session.flush()
    return obj


if __name__ == "__main__":
    main()
