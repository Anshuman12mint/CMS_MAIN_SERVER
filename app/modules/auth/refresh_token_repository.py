from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_active_by_token_hash(self, token_hash: str, now: datetime) -> RefreshToken | None:
        statement = (
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .where(RefreshToken.revoked_at.is_(None))
            .where(RefreshToken.expires_at > now)
        )
        return self.session.scalar(statement)

    def find_active_by_user_id(self, user_id: int, now: datetime) -> list[RefreshToken]:
        statement = (
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(RefreshToken.revoked_at.is_(None))
            .where(RefreshToken.expires_at > now)
            .order_by(RefreshToken.issued_at.desc())
        )
        return list(self.session.scalars(statement))

    def save(self, refresh_token: RefreshToken) -> RefreshToken:
        self.session.add(refresh_token)
        self.session.flush()
        self.session.refresh(refresh_token)
        return refresh_token

    def revoke(self, refresh_token: RefreshToken, revoked_at: datetime) -> RefreshToken:
        refresh_token.revoked_at = revoked_at
        self.session.add(refresh_token)
        self.session.flush()
        return refresh_token

    def revoke_older_tokens(self, user_id: int, keep: int, revoked_at: datetime) -> None:
        active_tokens = self.find_active_by_user_id(user_id, revoked_at)
        for refresh_token in active_tokens[keep:]:
            refresh_token.revoked_at = revoked_at
            self.session.add(refresh_token)
        self.session.flush()

    def delete_expired(self, now: datetime) -> None:
        statement = delete(RefreshToken).where(RefreshToken.expires_at <= now).execution_options(synchronize_session=False)
        self.session.execute(statement)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(RefreshToken)) or 0)

