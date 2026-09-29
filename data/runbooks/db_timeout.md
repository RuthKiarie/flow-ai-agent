# Runbook: Database Connection Timeout

## Symptoms
- Applications throw OperationalError: connection timed out or pool exhaustion errors.
- High traffic spikes or slow-running queries locking the database.

## Troubleshooting Steps
1. **Check Database Metrics:** Inspect CPU utilization and active connection counts via the cloud monitoring console.
2. **Identify Slow Queries:** Run SELECT * FROM pg_stat_activity WHERE state = 'active'; to find long-running queries.
3. **Kill Rogue Processes:** Terminate blocking queries using pg_cancel_backend(pid) if necessary.
4. **Scale Connection Pool:** If traffic is normal, increase max_connections in the application configuration or scale up the database instance tier.
