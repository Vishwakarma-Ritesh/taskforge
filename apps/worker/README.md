# TaskForge Worker Service

FastAPI service with a background polling loop.

The worker connects to PostgreSQL, finds unprocessed tasks, and marks them as
processed. This gives the project a second independently deployed service and a
clear service dependency path for Kubernetes debugging.

## Endpoints

- `GET /health`: liveness endpoint.
- `GET /ready`: readiness endpoint that checks database connectivity.

