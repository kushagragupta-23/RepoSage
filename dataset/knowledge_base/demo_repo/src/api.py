from .auth import validate_bearer_header


def get_profile(authorization: str | None, user_id: str) -> dict:
    """Example protected request flow used by the RepoSage demo."""
    token = validate_bearer_header(authorization)
    # A real application would decode and verify `token` before using user_id.
    return {"user_id": user_id, "authenticated": bool(token)}
