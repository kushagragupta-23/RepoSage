from hashlib import sha256
import hmac


def hash_password(password: str, salt: str) -> str:
    return sha256(f"{salt}:{password}".encode()).hexdigest()


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    actual = hash_password(password, salt)
    return hmac.compare_digest(actual, expected_hash)
