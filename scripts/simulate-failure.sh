#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${NAMESPACE:-devops-challenge}"

kubectl -n "${NAMESPACE}" patch configmap taskforge-config \
  --type merge \
  -p '{"data":{"DB_HOST":"wrong-postgres"}}'

kubectl -n "${NAMESPACE}" delete pod -l app.kubernetes.io/name=backend --wait=false
kubectl -n "${NAMESPACE}" delete pod -l app.kubernetes.io/name=worker --wait=false

echo "Injected failure: DB_HOST=wrong-postgres."
echo "New backend and worker pods should run but fail readiness because PostgreSQL is unreachable."
sleep 8

kubectl -n "${NAMESPACE}" get pods -o wide
kubectl -n "${NAMESPACE}" get endpoints backend-service

