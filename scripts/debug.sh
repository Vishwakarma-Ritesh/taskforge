#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${NAMESPACE:-devops-challenge}"

echo "Pods"
kubectl -n "${NAMESPACE}" get pods -o wide

echo
echo "Deployments"
kubectl -n "${NAMESPACE}" get deployments

echo
echo "Services"
kubectl -n "${NAMESPACE}" get svc

echo
echo "ConfigMap"
kubectl -n "${NAMESPACE}" get configmap taskforge-config -o yaml

echo
echo "Recent events"
kubectl -n "${NAMESPACE}" get events --sort-by=.lastTimestamp | tail -25

BACKEND_POD="$(kubectl -n "${NAMESPACE}" get pod -l app.kubernetes.io/name=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)"

if [[ -n "${BACKEND_POD}" ]]; then
  echo
  echo "Describe backend pod: ${BACKEND_POD}"
  kubectl -n "${NAMESPACE}" describe pod "${BACKEND_POD}"

  echo
  echo "Backend logs"
  kubectl -n "${NAMESPACE}" logs "${BACKEND_POD}" --tail=100 || true

  echo
  echo "Backend DB environment"
  kubectl -n "${NAMESPACE}" exec "${BACKEND_POD}" -- sh -c 'env | sort | grep "^DB_"' || true

  echo
  echo "DNS checks from backend pod"
  kubectl -n "${NAMESPACE}" exec "${BACKEND_POD}" -- sh -c 'getent hosts postgres-service || true; getent hosts wrong-postgres || true' || true
fi


echo
echo "Metrics, if metrics-server is available"
kubectl -n "${NAMESPACE}" top pods || true
