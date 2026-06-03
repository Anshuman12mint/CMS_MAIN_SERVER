from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Lock

from fastapi import HTTPException, status

from app.core.config import get_settings, utc_now


@dataclass
class AttemptWindow:
    failures: deque[datetime] = field(default_factory=deque)
    locked_until: datetime | None = None


class LoginRateLimiter:
    def __init__(self) -> None:
        self.lock = Lock()
        self.windows: dict[str, AttemptWindow] = {}

    def ensure_allowed(self, key: str) -> None:
        with self.lock:
            now = utc_now()
            window = self.windows.get(key)
            if window is None:
                return
            self._trim(window, now)
            if window.locked_until is not None and window.locked_until > now:
                seconds_remaining = int((window.locked_until - now).total_seconds())
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many failed login attempts. Try again in {max(seconds_remaining, 1)} seconds",
                )
            if window.locked_until is not None and window.locked_until <= now:
                window.locked_until = None
                if not window.failures:
                    self.windows.pop(key, None)

    def record_failure(self, key: str) -> None:
        settings = get_settings()
        with self.lock:
            now = utc_now()
            window = self.windows.setdefault(key, AttemptWindow())
            self._trim(window, now)
            window.failures.append(now)
            if len(window.failures) >= settings.login_rate_limit_max_attempts:
                window.locked_until = now + timedelta(seconds=settings.login_rate_limit_lockout_seconds)
                window.failures.clear()

    def record_success(self, key: str) -> None:
        with self.lock:
            self.windows.pop(key, None)

    def reset(self) -> None:
        with self.lock:
            self.windows.clear()

    def _trim(self, window: AttemptWindow, now: datetime) -> None:
        cutoff = now - timedelta(seconds=get_settings().login_rate_limit_window_seconds)
        while window.failures and window.failures[0] < cutoff:
            window.failures.popleft()


login_rate_limiter = LoginRateLimiter()

