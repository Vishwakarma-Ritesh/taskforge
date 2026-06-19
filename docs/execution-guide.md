# TaskForge Execution Guide

TaskForge has two microservices and one dependency:

- Backend API: FastAPI service with `/health`, `/ready`, `/items`, and `POST /items`.
- Worker service: polls PostgreSQL and marks rows as processed.
- PostgreSQL: the only service dependency.

Use this guide from a Mac terminal.

## 1. Local Prerequisites

Install and verify Docker Desktop:

```bash
docker --version
docker compose version
docker ps
```

Install Kind and kubectl:

```bash
brew install kind kubectl
kind version
kubectl version --client
```

Install Python for local tests:

```bash
brew install python
python3 --version
python3 -m venv .venv
source .venv/bin/activate
pip install -r apps/backend/requirements.txt
pip install -r apps/worker/requirements.txt
pytest apps/backend/src/tests apps/worker/src/tests
```

Azure DevOps/GitHub setup:

```bash
git init
git add .
git commit -m "Initial TaskForge DevOps challenge project"
```

Use GitHub or Azure Repos for source hosting. Use Azure DevOps pipelines from
the `pipelines/` directory. For local Kind deployment from a pipeline, use a
self-hosted Azure DevOps agent on your Mac because Microsoft-hosted agents
cannot access your laptop's Kind cluster.

Docker registry setup:

```bash
docker login
```

Pipeline image variables live in the YAML files:

```yaml
backendImageRepository: "your-dockerhub-user/taskforge-backend"
workerImageRepository: "your-dockerhub-user/taskforge-worker"
dockerRegistryServiceConnection: "dockerhub-service-connection"
```

## 2. Local Application Run

Run PostgreSQL, backend, and worker:

```bash
docker compose up --build
```

Verify services:

```bash
docker compose ps
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
curl -X POST http://127.0.0.1:8000/items \
  -H "Content-Type: application/json" \
  -d '{"title":"compose-item","description":"created locally"}'
curl http://127.0.0.1:8000/items
```

Confirm backend is connected to PostgreSQL:

```bash
docker compose exec postgres psql -U taskforge_user -d taskforge -c "SELECT id, title, processed FROM tasks ORDER BY id;"
```

Stop local stack:

```bash
docker compose down
```

## 3. Kind Kubernetes Setup

Create Kind cluster:

```bash
kind create cluster --name taskforge-dev --config infra/kind/kind-cluster.yaml
kind get clusters
kubectl cluster-info --context kind-taskforge-dev
kubectl get nodes -o wide
```

Build images:

```bash
docker build -t taskforge/backend:v1 apps/backend
docker build -t taskforge/worker:v1 apps/worker
```

Load images into Kind:

```bash
kind load docker-image taskforge/backend:v1 --name taskforge-dev
kind load docker-image taskforge/worker:v1 --name taskforge-dev
```

## 4. Kubernetes Deployment

Automated local path:

```bash
./scripts/deploy.sh
```

Manual raw YAML path:

```bash
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

Verify Kubernetes resources:

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

Verify app:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
curl -X POST http://127.0.0.1:8080/items \
  -H "Content-Type: application/json" \
  -d '{"title":"kind-item","description":"created in Kubernetes"}'
curl http://127.0.0.1:8080/items
```

## 5. PostgreSQL Connection

PostgreSQL is reached through this Kubernetes Service:

```text
postgres-service.devops-challenge.svc.cluster.local:5432
```

ConfigMap values:

```yaml
DB_HOST: postgres-service
DB_PORT: "5432"
DB_NAME: taskforge
```

Secret values:

```yaml
POSTGRES_USER: taskforge_user
POSTGRES_PASSWORD: taskforge_password
```

Verify DB env and DNS from backend pod:

```bash
BACKEND_POD=$(kubectl -n devops-challenge get pod -l app.kubernetes.io/name=backend -o jsonpath='{.items[0].metadata.name}')
kubectl -n devops-challenge exec "$BACKEND_POD" -- sh -c 'env | sort | grep "^DB_"'
kubectl -n devops-challenge exec "$BACKEND_POD" -- sh -c 'getent hosts postgres-service'
```

Exec into PostgreSQL:

```bash
kubectl -n devops-challenge exec -it deployment/postgres -- sh
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

One-line query:

```bash
kubectl -n devops-challenge exec deployment/postgres -- \
  psql -U taskforge_user -d taskforge -c "SELECT id, title, processed FROM tasks ORDER BY id;"
```

## 6. CI/CD Setup

Pipeline folders:

```text
pipelines/Infra-Pipelines
pipelines/Service-CI
pipelines/Service-CD
pipelines/Master-Pipelines
```

Infra pipelines validate and apply shared Kubernetes resources. Service CI
pipelines install dependencies, test, build Docker images, and push images.
Service CD pipelines apply raw Kubernetes YAML and verify rollouts. The master
pipeline does the full flow: test, build, push, deploy, verify.

Configure Azure DevOps:

1. Create Docker registry service connection named `dockerhub-service-connection`.
2. Create self-hosted agent pool named `SelfHosted-Kind`.
3. Run the agent on your Mac with Docker, Kind, and kubectl available.
4. Create pipeline from `pipelines/Master-Pipelines/CICD-DevOps-Challenge-MasterPipeline.yml`.

Verify after pipeline run:

```bash
kubectl -n devops-challenge get pods -o wide
kubectl -n devops-challenge rollout status deployment/backend
kubectl -n devops-challenge rollout status deployment/worker
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
```

## 7. Monitoring and Observability

Free Kubernetes-native observability:

```bash
kubectl -n devops-challenge logs deployment/backend --tail=100
kubectl -n devops-challenge logs deployment/worker --tail=100
kubectl -n devops-challenge describe pod <pod-name>
kubectl -n devops-challenge get events --sort-by=.lastTimestamp
```

Optional metrics-server:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl -n kube-system patch deployment metrics-server --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
kubectl -n kube-system rollout status deployment/metrics-server --timeout=180s
kubectl -n devops-challenge top pods
```

## 8. Reliability Improvement

Chosen improvement: readiness and liveness probes.

- `/health`: process is alive.
- `/ready`: application can connect to PostgreSQL.

This protects SLA because Kubernetes does not send traffic to pods that are
Running but NotReady.

Tradeoff: aggressive probes can restart healthy pods or delay rollouts.

## 9. Failure Simulation

Break DB host:

```bash
./scripts/simulate-failure.sh
```

Debug:

```bash
kubectl get pods -n devops-challenge
kubectl describe pod <backend-pod> -n devops-challenge
kubectl logs <backend-pod> -n devops-challenge
kubectl get configmap taskforge-config -n devops-challenge -o yaml
kubectl get svc -n devops-challenge
```

Root cause: `DB_HOST=wrong-postgres` but the real Service is `postgres-service`.

Fix:

```bash
./scripts/fix-failure.sh
curl http://127.0.0.1:8080/ready
```

## 10. Video Flow

Live demo: deploy, show pods/services/PVC, call `/health`, `/ready`, and
`/items`.

Architecture: explain Kind, namespace, ConfigMap, Secret, PostgreSQL Service,
PVC, backend Deployment, worker Deployment, Service, and Ingress.

Failure debugging: inject wrong `DB_HOST`, inspect pods, describe, logs,
ConfigMap, Services, root cause, fix, verify.

Tradeoffs: Kind, NodePort, in-cluster PostgreSQL, demo Secret, no GitOps, no
managed database. Production improvements: managed PostgreSQL, Vault,
Prometheus/Grafana, Argo CD, HPA, NetworkPolicies, canary deployments.

## 11. Troubleshooting

ImagePullBackOff:

```bash
kind load docker-image taskforge/backend:v1 --name taskforge-dev
kind load docker-image taskforge/worker:v1 --name taskforge-dev
kubectl -n devops-challenge rollout restart deployment/backend deployment/worker
```

CrashLoopBackOff:

```bash
kubectl -n devops-challenge describe pod <pod-name>
kubectl -n devops-challenge logs <pod-name> --previous
```

Pod Pending:

```bash
kubectl -n devops-challenge describe pod <pod-name>
kubectl -n devops-challenge get pvc
kubectl get nodes
```

Readiness probe failing or DB connection refused:

```bash
kubectl -n devops-challenge get svc postgres-service
kubectl -n devops-challenge get configmap taskforge-config -o yaml
kubectl -n devops-challenge logs deployment/backend --tail=100
```

Ingress not working: use NodePort for the demo.

```bash
curl http://127.0.0.1:8080/health
```

Pipeline authentication failure: check Docker registry service connection, image
repository names, and self-hosted agent pool name.
