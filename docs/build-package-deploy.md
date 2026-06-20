# Build, Package, and Deploy

## Build

Install dependencies and run static validation:

```bash
pip install -r apps/backend/requirements.txt
pip install -r apps/worker/requirements.txt
ruff check apps/backend/src apps/worker/src
pytest apps/backend/src/tests apps/worker/src/tests
```

## Package

Build Docker images locally:

```bash
docker build -t taskforge/backend:v1 apps/backend
docker build -t taskforge/worker:v1 apps/worker
```

For Kind, load images into the local Kubernetes cluster:

```bash
kind load docker-image taskforge/backend:v1 --name taskforge
kind load docker-image taskforge/worker:v1 --name taskforge
```

For CI/CD with Docker Hub, tag and push images:

```bash
docker tag taskforge/backend:v1 vishwakarmaritesh08/taskforge-backend:v1
docker tag taskforge/worker:v1 vishwakarmaritesh08/taskforge-worker:v1

docker push vishwakarmaritesh08/taskforge-backend:v1
docker push vishwakarmaritesh08/taskforge-worker:v1
```

## Deploy

Apply raw Kubernetes manifests:

```bash
kubectl apply -f infra/k8s/
```

Verify rollouts:

```bash
kubectl -n devops-challenge rollout status deployment/postgres
kubectl -n devops-challenge rollout status deployment/backend
kubectl -n devops-challenge rollout status deployment/worker
```

## Verify

For local Kind testing, start port forwarding first:

```bash
kubectl port-forward svc/backend-service 8080:80 -n devops-challenge
```

Then verify the application:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
curl http://127.0.0.1:8080/items
```

Create a test item:

```bash
curl -X POST http://127.0.0.1:8080/items \
  -H "Content-Type: application/json" \
  -d '{"title":"deploy-doc-item","description":"created during deployment verification"}'
```

Confirm worker processing:

```bash
curl http://127.0.0.1:8080/items
```

Expected result:

```json
"processed": true
```