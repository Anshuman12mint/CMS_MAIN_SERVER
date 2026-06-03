from __future__ import annotations

from datetime import timedelta
from typing import Any

import jwt

from app.core.config import get_settings, utc_now


class JwtService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_token(self, login_id: str, role: str) -> str:
        now = utc_now()
        payload = {
            "sub": login_id,
            "role": role,
            "iss": self.settings.jwt_issuer,
            "aud": self.settings.jwt_audience,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self.settings.jwt_expiration_minutes)).timestamp()),
        }
        return jwt.encode(payload, self.settings.jwt_secret, algorithm="HS256")

    def extract_login_id(self, token: str) -> str:
        return str(self.parse_claims(token).get("sub", ""))

    def is_token_valid(self, token: str, expected_login_id: str) -> bool:
        claims = self.parse_claims(token)
        return claims.get("sub") == expected_login_id

    def parse_claims(self, token: str) -> dict[str, Any]:
        return jwt.decode(
            token,
            self.settings.jwt_secret,
            algorithms=["HS256"],
            audience=self.settings.jwt_audience,
            issuer=self.settings.jwt_issuer,
            leeway=self.settings.jwt_leeway_seconds,
        )

