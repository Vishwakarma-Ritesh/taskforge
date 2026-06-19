# Failure Debugging Walkthrough

## Failure

The failure is a database connectivity issue caused by a bad environment value:

```bash
DB_HOST=wrong-postgres
```

Correct value:

```bash
DB_HOST=postgres-service
```

Run:

```bash
./scripts/simulate-failure.sh
```

## Symptoms

- Backend pods are running.
- `/health` passes when called directly on the pod.
- `/ready` fails because PostgreSQL cannot be reached.
- Readiness probe fails.
- Kubernetes removes not-ready pods from Service endpoints.
- Logs show database connection errors.

## Debugging Methodology

### 1. Observe Pod State

```bash
kubectl get pods -n devops-challenge
```

Look for `0/1` readiness on backend or worker pods.

### 2. Describe the Backend Pod

```bash
kubectl describe pod <backend-pod> -n devops-challenge
```

Look for readiness probe failures and recent events.

### 3. Check Logs

```bash
kubectl logs <backend-pod> -n devops-challenge
```

Expected signal:

```text
Readiness check failed
could not translate host name "wrong-postgres"
```

### 4. Inspect ConfigMap

```bash
kubectl get configmap taskforge-config -n devops-challenge -o yaml
```

Expected broken value:

```yaml
DB_HOST: wrong-postgres
```

### 5. Inspect Services

```bash
kubectl get svc -n devops-challenge
```

The real database Service is:

```bash
postgres-service
```

### 6. Verify Environment from the Pod

```bash
kubectl exec -it <backend-pod> -n devops-challenge -- sh
env | sort | grep DB_
getent hosts postgres-service
getent hosts wrong-postgres
```

### 7. Root Cause

The application was configured to connect to a non-existent Kubernetes Service.
The process was alive, but the application was not ready to serve traffic.

### 8. Fix

```bash
./scripts/fix-failure.sh
```

Or manually:

```bash
kubectl -n devops-challenge patch configmap taskforge-config \
  --type merge \
  -p '{"data":{"DB_HOST":"postgres-service"}}'
kubectl rollout restart deployment/backend -n devops-challenge
kubectl rollout status deployment/backend -n devops-challenge
```

### 9. Validate Recovery

```bash
kubectl get pods -n devops-challenge
curl http://127.0.0.1:8080/ready
```

Expected:

```json
{"status":"ready","database":"reachable"}
```

## Wrong Assumption to Mention in Video

At first, it is tempting to assume the pod is healthy because it is in `Running`
state. The important lesson is that `Running` only means the container process
started. It does not prove the application can serve traffic.

