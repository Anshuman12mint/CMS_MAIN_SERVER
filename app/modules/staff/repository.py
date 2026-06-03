from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.staff.model import Staff


class StaffRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, staff_id: int | None) -> Staff | None:
        return None if staff_id is None else self.session.get(Staff, staff_id)

    def find_by_staff_code(self, staff_code: str | None) -> Staff | None:
        if staff_code is None:
            return None
        return self.session.scalar(select(Staff).where(func.lower(Staff.staff_code) == staff_code.strip().lower()))

    def exists_by_id(self, staff_id: int | None) -> bool:
        if staff_id is None:
            return False
        return bool(self.session.scalar(select(func.count()).select_from(Staff).where(Staff.staff_id == staff_id)))

    def exists_by_staff_code(self, staff_code: str | None, exclude_staff_id: int | None = None) -> bool:
        if staff_code is None:
            return False
        statement = select(func.count()).select_from(Staff).where(func.lower(Staff.staff_code) == staff_code.strip().lower())
        if exclude_staff_id is not None:
            statement = statement.where(Staff.staff_id != exclude_staff_id)
        return bool(self.session.scalar(statement))

    def find_all(self) -> list[Staff]:
        return list(self.session.scalars(select(Staff).order_by(Staff.last_name.asc(), Staff.first_name.asc())))

    def save(self, staff: Staff) -> Staff:
        self.session.add(staff)
        self.session.flush()
        self.session.refresh(staff)
        return staff

    def delete(self, staff: Staff) -> None:
        self.session.delete(staff)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Staff)) or 0)

