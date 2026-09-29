# API Reference

## GET /profile

Requires `Authorization: Bearer <token>`. The request is validated by `validate_bearer_header`, decoded by the authentication layer, and then the profile handler loads the user record.

## GET /health

Returns a lightweight service-health response. It should not expose credentials, database URLs, or token secrets.
