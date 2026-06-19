#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER_NAME="${CLUSTER_NAME:-taskforge-dev}"
NAMESPACE="${NAMESPACE:-devops-challenge}"
IMAGE_TAG="${IMAGE_TAG:-v1}"

for command in docker kind kubectl; do
  if ! command -v "${command}" >/dev/null 2>&1; then
    echo "${command} is required. Install it before running this script."
    exit 1
  fi
done

if ! kind get clusters | grep -qx "${CLUSTER_NAME}"; then
  kind create cluster --name "${CLUSTER_NAME}" --config "${ROOT_DIR}/infra/kind/kind-cluster.yaml"
fi

docker build -t "taskforge/backend:${IMAGE_TAG}" "${ROOT_DIR}/apps/backend"
docker build -t "taskforge/worker:${IMAGE_TAG}" "${ROOT_DIR}/apps/worker"

kind load docker-image "taskforge/backend:${IMAGE_TAG}" --name "${CLUSTER_NAME}"
kind load docker-image "taskforge/worker:${IMAGE_TAG}" --name "${CLUSTER_NAME}"

kubectl apply -f "${ROOT_DIR}/infra/k8s/"

if [[ "${IMAGE_TAG}" != "v1" ]]; then
  kubectl -n "${NAMESPACE}" set image deployment/backend backend="taskforge/backend:${IMAGE_TAG}"
  kubectl -n "${NAMESPACE}" set image deployment/worker worker="taskforge/worker:${IMAGE_TAG}"
fi

kubectl -n "${NAMESPACE}" rollout status deployment/postgres --timeout=180s
kubectl -n "${NAMESPACE}" rollout status deployment/backend --timeout=180s
kubectl -n "${NAMESPACE}" rollout status deployment/worker --timeout=180s

kubectl -n "${NAMESPACE}" get pods -o wide
kubectl -n "${NAMESPACE}" get svc
kubectl -n "${NAMESPACE}" get ingress

echo "TaskForge is deployed to Kind."
echo "Backend service is reachable at http://127.0.0.1:8080 through Kind nodePort mapping."
echo "Try: curl http://127.0.0.1:8080/health"
