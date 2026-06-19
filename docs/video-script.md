# TaskForge Video Script

Target length: 8-12 minutes.

## 0:00 to 0:45 - Introduction

Say:

```text
This project is TaskForge. It is a minimal production-style application stack built to demonstrate DevOps infrastructure skills. The app has two microservices: a FastAPI backend API and a FastAPI worker service. PostgreSQL is the only dependency.

The application logic is simple by design. The focus is containerization, Kind Kubernetes, raw YAML manifests, CI/CD automation, probes, observability, and operational debugging.
```

## 0:45 to 4:00 - Live Demo

Show project structure:

```bash
tree -L 3
```

Deploy to Kind:

```bash
./scripts/deploy.sh
```

Show Kubernetes resources:

```bash
kubectl -n devops-challenge get pods -o wide
kubectl -n devops-challenge get deployments
kubectl -n devops-challenge get svc
kubectl -n devops-challenge get pvc
kubectl -n devops-challenge get ingress
```

Show the application working:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
curl -X POST http://127.0.0.1:8080/items \
  -H "Content-Type: application/json" \
  -d '{"title":"video-item","description":"created during demo"}'
curl http://127.0.0.1:8080/items
```

Say:

```text
This proves the application is working end-to-end. The backend accepts traffic, PostgreSQL stores the item, and the worker processes rows asynchronously.
```

Show CI/CD files:

```text
pipelines/Master-Pipelines/CICD-DevOps-Challenge-MasterPipeline.yml
pipelines/Service-CI/CI-Backend-Pipeline.yml
pipelines/Service-CD/CD-Backend-Pipeline.yml
```

Say:

```text
The master pipeline runs the complete flow: install dependencies, run tests, build Docker images, push to registry, apply Kubernetes YAML, and verify rollout status.
```

## 4:00 to 6:30 - Architecture Walkthrough

Show:

```bash
docs/proposal.md
docs/architecture.md
infra/k8s/
```

Say:

```text
The cluster is local Kind, which keeps the project free while still using real Kubernetes. The namespace is devops-challenge. The backend service exposes /health, /ready, and /items. PostgreSQL is reached through the Kubernetes Service postgres-service. DB_HOST and DB_NAME come from the ConfigMap, while DB_USER and DB_PASSWORD come from the Secret.

The backend has two replicas to show a realistic deployment. The worker is deployed independently. PostgreSQL uses a PVC. All Kubernetes objects are written as raw YAML.
```

Explain reliability:

```text
I chose readiness and liveness probes because a pod can be Running but not actually ready to serve traffic. /health proves the process is alive. /ready proves the app can reach PostgreSQL. This protects SLA because Kubernetes removes NotReady pods from service endpoints.
```

## 6:30 to 9:30 - Failure Debugging Walkthrough

Inject failure:

```bash
./scripts/simulate-failure.sh
```

Say:

```text
I intentionally changed DB_HOST from postgres-service to wrong-postgres. This simulates a real production configuration incident.
```

Show symptoms:

```bash
kubectl get pods -n devops-challenge
kubectl describe pod <backend-pod> -n devops-challenge
kubectl logs <backend-pod> -n devops-challenge
kubectl get configmap taskforge-config -n devops-challenge -o yaml
kubectl get svc -n devops-challenge
```

Say:

```text
The pod is Running, so the container process started. But it is NotReady, so Kubernetes will not send traffic to it. Logs show a database connection problem. The ConfigMap shows DB_HOST is wrong-postgres, while kubectl get svc shows the real database Service is postgres-service.
```

Fix:

```bash
./scripts/fix-failure.sh
curl http://127.0.0.1:8080/ready
```

Say:

```text
After restoring DB_HOST to postgres-service and restarting the deployment, readiness passes again. The root cause was bad runtime configuration, not a code bug.
```

## 9:30 to 11:30 - Tradeoffs

Say:

```text
I intentionally simplified by using Kind instead of cloud Kubernetes, NodePort instead of a cloud load balancer, in-cluster PostgreSQL instead of managed PostgreSQL, and demo secrets in YAML instead of an external secret manager.

At scale, PostgreSQL would be a single point of failure, manual kubectl apply could drift, and NodePort is not production-grade ingress.

In production I would add managed PostgreSQL, Vault or External Secrets, Prometheus and Grafana, Argo CD, HPA, NetworkPolicies, canary deployments, image scanning, and backup/restore testing.
```
