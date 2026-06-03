from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def import_models() -> None:
    """Import SQLAlchemy models here as modules are ported."""
    from app.modules.auth.models import RefreshToken  # noqa: F401
    from app.modules.attendance.model import Attendance  # noqa: F401
    from app.modules.courses.model import Course  # noqa: F401
    from app.modules.fees.model import Fee  # noqa: F401
    from app.modules.marks.model import StudentMark  # noqa: F401
    from app.modules.staff.model import Staff  # noqa: F401
    from app.modules.students.model import Student  # noqa: F401
    from app.modules.subjects.model import Subject  # noqa: F401
    from app.modules.teachers.model import Teacher, TeacherCourse, TeacherSubject  # noqa: F401
    from app.modules.users.model import User  # noqa: F401
