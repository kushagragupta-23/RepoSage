# Deployment Guide

The service is deployed behind a reverse proxy. Environment variables provide `DATABASE_URL`, `JWT_SECRET`, and optional token-expiry overrides.

## Health checks

- `/health` verifies that the API process is alive.
- A database readiness check should be used before routing production traffic.
- When database timeouts appear after deployment, first compare pool size and connection limits with the target database.

## Safe configuration

Secrets must be injected through the deployment environment. Do not commit `.env` files or private keys to the repository.
