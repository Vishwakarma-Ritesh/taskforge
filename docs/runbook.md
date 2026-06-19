# TaskForge Runbook

## Common Checks

```bash
kubectl -n devops-challenge get pods -o wide
kubectl -n devops-challenge get deployments
kubectl -n devops-challenge get svc
kubectl -n devops-challenge get endpoints
kubectl -n devops-challenge get events --sort-by=.lastTimestamp
```

## Rollout Status

```bash
kubectl -n devops-challenge rollout status deployment/postgres
kubectl -n devops-challenge rollout status deployment/backend
kubectl -n devops-challenge rollout status deployment/worker
```

## Logs

```bash
kubectl -n devops-challenge logs deployment/backend --tail=100
kubectl -n devops-challenge logs deployment/worker --tail=100
kubectl -n devops-challenge logs deployment/postgres --tail=100
```

## Restart

```bash
kubectl -n devops-challenge rollout restart deployment/backend
kubectl -n devops-challenge rollout restart deployment/worker
```

## Rollback

```bash
kubectl -n devops-challenge rollout history deployment/backend
kubectl -n devops-challenge rollout undo deployment/backend
kubectl -n devops-challenge rollout status deployment/backend
```

## API Test

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
curl -X POST http://127.0.0.1:8080/items \
  -H "Content-Type: application/json" \
  -d '{"title":"runbook-task","description":"created during runbook test"}'
curl http://127.0.0.1:8080/items
```

## Database Access

```bash
kubectl -n devops-challenge exec -it deployment/postgres -- sh
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Useful SQL:

```sql
SELECT id, title, processed, created_at, processed_at FROM tasks ORDER BY id;
```
