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

Build Docker images:

```bash
docker build -t taskforge/backend:v1 apps/backend
docker build -t taskforge/worker:v1 apps/worker
```

For Kind, load images into the cluster:

```bash
kind load docker-image taskforge/backend:v1 --name taskforge-dev
kind load docker-image taskforge/worker:v1 --name taskforge-dev
```

For CI/CD, push images to a registry:

```bash
docker tag taskforge/backend:v1 your-dockerhub-user/taskforge-backend:v1
docker tag taskforge/worker:v1 your-dockerhub-user/taskforge-worker:v1
docker push your-dockerhub-user/taskforge-backend:v1
docker push your-dockerhub-user/taskforge-worker:v1
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

```bash
kubectl -n devops-challenge get pods -o wide
kubectl -n devops-challenge get svc
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
curl -X POST http://127.0.0.1:8080/items \
  -H "Content-Type: application/json" \
  -d '{"title":"deploy-doc-item","description":"created during deployment verification"}'
curl http://127.0.0.1:8080/items
```
