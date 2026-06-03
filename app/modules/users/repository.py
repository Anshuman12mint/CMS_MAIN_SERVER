from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.users.model import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, user_id: int | None) -> User | None:
        return None if user_id is None else self.session.get(User, user_id)

    def find_by_login_id(self, login_id: str | None) -> User | None:
        if login_id is None:
            return None
        return self.session.scalar(select(User).where(func.lower(User.login_id) == login_id.strip().lower()))

    def find_all_ordered(self) -> list[User]:
        return list(self.session.scalars(select(User).order_by(User.created_at.desc())))

    def exists_by_login_id(self, login_id: str | None, exclude_user_id: int | None = None) -> bool:
        if login_id is None:
            return False
        statement = select(func.count()).select_from(User).where(func.lower(User.login_id) == login_id.strip().lower())
        if exclude_user_id is not None:
            statement = statement.where(User.user_id != exclude_user_id)
        return bool(self.session.scalar(statement))

    def exists_by_email(self, email: str | None, exclude_user_id: int | None = None) -> bool:
        if email is None:
            return False
        statement = select(func.count()).select_from(User).where(func.lower(User.email) == email.strip().lower())
        if exclude_user_id is not None:
            statement = statement.where(User.user_id != exclude_user_id)
        return bool(self.session.scalar(statement))

    def exists_by_student_id(self, student_id: int | None, exclude_user_id: int | None = None) -> bool:
        return self._exists_by_profile_id(User.student_id, student_id, exclude_user_id)

    def exists_by_teacher_id(self, teacher_id: int | None, exclude_user_id: int | None = None) -> bool:
        return self._exists_by_profile_id(User.teacher_id, teacher_id, exclude_user_id)

    def exists_by_staff_id(self, staff_id: int | None, exclude_user_id: int | None = None) -> bool:
        return self._exists_by_profile_id(User.staff_id, staff_id, exclude_user_id)

    def save(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        self.session.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.session.delete(user)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(User)) or 0)

    def _exists_by_profile_id(self, column, profile_id: int | None, exclude_user_id: int | None) -> bool:
        if profile_id is None:
            return False
        statement = select(func.count()).select_from(User).where(column == profile_id)
        if exclude_user_id is not None:
            statement = statement.where(User.user_id != exclude_user_id)
        return bool(self.session.scalar(statement))

