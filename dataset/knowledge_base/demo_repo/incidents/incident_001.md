# Incident 001 - Intermittent Database Timeouts

During a load test, several profile requests failed with database pool timeout errors. The database itself remained reachable.

## Findings

- Application pool size was 5 connections.
- Concurrent requests briefly exceeded the available pool.
- Increasing API worker count without increasing database capacity made the issue more frequent.

## Resolution

The team reduced worker concurrency for the demo environment, kept the pool timeout at 10 seconds, and added monitoring for active connections.
