from dataclasses import dataclass

@dataclass
class User:
    user_id: int
    email: str
    is_active: bool = True


def get_user_by_id(user_id: int) -> User | None:
    """Demo lookup used by the protected profile endpoint."""
    if user_id == 1:
        return User(user_id=1, email="demo@example.com", is_active=True)
    return None


def require_active_user(user: User) -> User:
    if not user.is_active:
        raise PermissionError("Inactive users cannot access protected resources")
    return user
