from __future__ import annotations

from collections.abc import Callable
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.modules.auth.jwt import JwtService
from app.modules.users.model import User
from app.modules.users.repository import UserRepository


bearer_scheme = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


def authenticate_token(token: str, session: Session) -> User | None:
    if not token:
        return None
    try:
        jwt_service = JwtService()
        login_id = jwt_service.extract_login_id(token)
        if not login_id:
            return None
        user = UserRepository(session).find_by_login_id(login_id)
        if user is None:
            return None
        if not jwt_service.is_token_valid(token, user.login_id):
            return None
        return user
    except InvalidTokenError:
        logger.warning("token_validation_failed")
        return None
    except SQLAlchemyError:
        logger.exception("token_user_lookup_failed")
        return None
    except Exception:
        logger.exception("token_authentication_failed")
        return None


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_db_session),
) -> User | None:
    if credentials is None or credentials.scheme.lower() != "bearer":
        return None
    return authenticate_token(credentials.credentials.strip(), session)


def get_current_user(current_user: User | None = Depends(get_optional_current_user)) -> User:
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication is required")
    return current_user


def require_roles(*roles: str) -> Callable:
    normalized_roles = {role.strip().upper() for role in roles}

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        role = (current_user.role or "").strip().upper()
        if role not in normalized_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access is denied")
        return current_user

    return dependency

