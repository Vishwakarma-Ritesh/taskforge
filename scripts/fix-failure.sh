#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${NAMESPACE:-devops-challenge}"

kubectl -n "${NAMESPACE}" patch configmap taskforge-config \
  --type merge \
  -p '{"data":{"DB_HOST":"postgres-service"}}'

kubectl -n "${NAMESPACE}" rollout restart deployment/backend deployment/worker
kubectl -n "${NAMESPACE}" rollout status deployment/backend --timeout=180s
kubectl -n "${NAMESPACE}" rollout status deployment/worker --timeout=180s

kubectl -n "${NAMESPACE}" get pods -o wide
kubectl -n "${NAMESPACE}" get endpoints backend-service

echo "Failure fixed: DB_HOST=postgres-service."
