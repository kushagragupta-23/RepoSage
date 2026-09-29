from src.auth import validate_bearer_header


def test_validate_bearer_header_accepts_bearer_token():
    assert validate_bearer_header("Bearer abc123") == "abc123"


def test_validate_bearer_header_rejects_missing_prefix():
    try:
        validate_bearer_header("abc123")
    except ValueError:
        assert True
    else:
        assert False
