# Demo Service Architecture

The service has three layers:

1. **API layer** (`src/api.py`) receives HTTP requests and validates the Bearer header.
2. **Authentication layer** (`src/auth.py`) creates access-token claims and validates the header format.
3. **Configuration/database layer** (`src/config.py`, `src/database.py`) reads token-expiry and database settings from environment variables.

## Authentication flow

A client sends `Authorization: Bearer <token>`. The API forwards the header to `validate_bearer_header`. Token claims are created by `create_access_token`. The expiration window comes from `ACCESS_TOKEN_EXPIRE_MINUTES`, whose default is 30 minutes in `src/config.py`.

## Database flow

`src/config.py` reads `DATABASE_URL` and `DB_POOL_SIZE`. `DatabaseSettings` exposes those values to the database layer. A timeout can be caused by an unreachable database host, DNS/network problems, or an exhausted connection pool. Credentials errors are a different failure category and should not be described as a timeout without evidence.
