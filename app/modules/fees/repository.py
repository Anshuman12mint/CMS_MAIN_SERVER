from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.fees.model import Fee


class FeeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, fee_id: int | None) -> Fee | None:
        return None if fee_id is None else self.session.get(Fee, fee_id)

    def find_by_student_id_ordered(self, student_id: int) -> list[Fee]:
        return list(self.session.scalars(select(Fee).where(Fee.student_id == student_id).order_by(Fee.due_date.desc())))

    def find_all_ordered(self) -> list[Fee]:
        return list(self.session.scalars(select(Fee).order_by(Fee.due_date.desc())))

    def save(self, fee: Fee) -> Fee:
        self.session.add(fee)
        self.session.flush()
        self.session.refresh(fee)
        return fee

    def delete(self, fee: Fee) -> None:
        self.session.delete(fee)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Fee)) or 0)

    def count_by_status(self, status: str) -> int:
        return int(
            self.session.scalar(select(func.count()).select_from(Fee).where(func.lower(Fee.status) == status.lower()))
            or 0
        )

    def sum_pending_amount(self) -> Decimal:
        value = self.session.scalar(select(func.coalesce(func.sum(Fee.amount), 0)).where(func.lower(Fee.status) == "pending"))
        return Decimal(value or 0)
