# Troubleshooting Runbook

## Database timeout

Symptoms include `ConnectionTimeoutError`, requests hanging during database access, or messages saying a connection could not be acquired from the pool.

Check in this order:

1. Verify `DATABASE_URL` points to the intended host/database.
2. Verify DNS/network reachability from the application environment.
3. Check whether all pooled connections are busy. The default `DB_POOL_SIZE` is 5.
4. Compare the failure with application logs before changing credentials.

## JWT expiry complaints

If users are logged out after roughly 30 minutes, check `ACCESS_TOKEN_EXPIRE_MINUTES`. The default is 30. A deployment can override it through the environment. Do not hard-code a longer expiry in `auth.py`; change the environment configuration and review the security requirement first.
