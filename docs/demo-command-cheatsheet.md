# TaskForge Demo Command Cheat Sheet

Use this when recording the 8-12 minute demo.

## Start

```bash
cd /Users/riteshvishwakarma/Downloads/project/TaskForge
```

## Prerequisite Checks

```bash
docker --version
docker compose version
kind version
kubectl version --client
python3 --version
```

## Local Docker Compose

```bash
docker compose up --build
```

In another terminal:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
curl -X POST http://127.0.0.1:8000/items \
  -H "Content-Type: application/json" \
  -d '{"title":"compose-item","description":"created locally"}'
curl http://127.0.0.1:8000/items
docker compose exec postgres psql -U taskforge_user -d taskforge -c "SELECT id, title, processed FROM tasks ORDER BY id;"
```

Stop:

```bash
docker compose down
```

## Kind Deploy

```bash
./scripts/deploy.sh
```

Manual equivalent:

```bash
kind create cluster --name taskforge-dev --config infra/kind/kind-cluster.yaml
docker build -t taskforge/backend:v1 apps/backend
docker build -t taskforge/worker:v1 apps/worker
kind load docker-image taskforge/backend:v1 --name taskforge-dev
kind load docker-image taskforge/worker:v1 --name taskforge-dev
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/configmap.yaml
kubectl apply -f infra/k8s/secret.yaml
kubectl apply -f infra/k8s/postgres.yaml
kubectl apply -f infra/k8s/backend-deployment.yaml
kubectl apply -f infra/k8s/backend-service.yaml
kubectl apply -f infra/k8s/worker-deployment.yaml
kubectl apply -f infra/k8s/worker-service.yaml
kubectl apply -f infra/k8s/ingress.yaml
```

## Kubernetes Verify

```bash
kubectl -n devops-challenge get pods -o wide
kubectl -n devops-challenge get deployments
kubectl -n devops-challenge get svc
kubectl -n devops-challenge get pvc
kubectl -n devops-challenge get ingress
kubectl -n devops-challenge rollout status deployment/postgres
kubectl -n devops-challenge rollout status deployment/backend
kubectl -n devops-challenge rollout status deployment/worker
```

## App Verify

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
curl -X POST http://127.0.0.1:8080/items \
  -H "Content-Type: application/json" \
  -d '{"title":"kind-item","description":"created in Kubernetes"}'
curl http://127.0.0.1:8080/items
```

## PostgreSQL Debug

```bash
BACKEND_POD=$(kubectl -n devops-challenge get pod -l app.kubernetes.io/name=backend -o jsonpath='{.items[0].metadata.name}')
kubectl -n devops-challenge exec "$BACKEND_POD" -- sh -c 'env | sort | grep "^DB_"'
kubectl -n devops-challenge exec "$BACKEND_POD" -- sh -c 'getent hosts postgres-service'
kubectl -n devops-challenge exec deployment/postgres -- psql -U taskforge_user -d taskforge -c "SELECT id, title, processed FROM tasks ORDER BY id;"
```

## Failure Demo

```bash
./scripts/simulate-failure.sh
BACKEND_POD=$(kubectl -n devops-challenge get pod -l app.kubernetes.io/name=backend -o jsonpath='{.items[0].metadata.name}')
kubectl get pods -n devops-challenge
kubectl describe pod "$BACKEND_POD" -n devops-challenge
kubectl logs "$BACKEND_POD" -n devops-challenge
kubectl get configmap taskforge-config -n devops-challenge -o yaml
kubectl get svc -n devops-challenge
./scripts/fix-failure.sh
curl http://127.0.0.1:8080/ready
```

## CI/CD Files to Show

```bash
pipelines/Infra-Pipelines/CICD-K8s-Infra-Pipeline.yml
pipelines/Infra-Pipelines/CICD-App-Dependencies-Pipeline.yml
pipelines/Service-CI/CI-Backend-Pipeline.yml
pipelines/Service-CI/CI-Worker-Pipeline.yml
pipelines/Service-CD/CD-Backend-Pipeline.yml
pipelines/Service-CD/CD-Worker-Pipeline.yml
pipelines/Master-Pipelines/CICD-DevOps-Challenge-MasterPipeline.yml
```
