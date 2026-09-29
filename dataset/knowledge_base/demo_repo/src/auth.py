from datetime import datetime, timedelta, timezone
from .config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM


def create_access_token(user_id: str, secret_key: str) -> dict:
    """Return the claims that would be encoded into a JWT."""
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
        "alg": JWT_ALGORITHM,
    }


def validate_bearer_header(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise ValueError("Missing or invalid Bearer token")
    return authorization.removeprefix("Bearer ").strip()
