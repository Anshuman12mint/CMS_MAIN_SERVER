from __future__ import annotations

from sqlalchemy.orm import Session

from app.common import helpers
from app.core.config import get_settings, utc_now
from app.core.security import hash_password
from app.modules.users.model import User
from app.modules.users.repository import UserRepository


class BootstrapAdminInitializer:
    def __init__(self, session: Session) -> None:
        self.user_repository = UserRepository(session)
        self.settings = get_settings()

    def run(self) -> None:
        if not self.settings.bootstrap_admin_enabled or self.user_repository.count() > 0:
            return

        username = helpers.trim_to_none(self.settings.bootstrap_admin_username)
        password = helpers.trim_to_none(self.settings.bootstrap_admin_password)
        email = helpers.trim_to_none(self.settings.bootstrap_admin_email)
        if not username or not password or not email:
            raise ValueError("Bootstrap admin properties must not be blank")

        admin = User()
        admin.login_id = helpers.normalize_code(username) or username
        admin.legacy_username = admin.login_id
        admin.password_hash = hash_password(password)
        admin.email = email.lower()
        admin.role = "Admin"
        admin.account_status = "ACTIVE"
        admin.registered_at = utc_now()
        self.user_repository.save(admin)

