# TaskForge Backend API

FastAPI service that exposes the public TaskForge API.

## Endpoints

- `GET /health`: liveness endpoint. It confirms the process can respond.
- `GET /ready`: readiness endpoint. It checks PostgreSQL connectivity.
- `GET /items`: lists stored work items.
- `POST /items`: creates a new work item.
- `GET /tasks`: compatibility alias for task-oriented naming.
- `POST /tasks`: compatibility alias for task-oriented naming.

## Database Connection

The service reads database configuration from environment variables injected by
Kubernetes ConfigMaps and Secrets:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
# Backend CI pipeline builds Docker image and pushes to registry
# Backend CI pipeline builds Docker image and pushes to registry
