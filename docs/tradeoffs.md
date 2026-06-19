# Tradeoff Discussion

## What Was Simplified

- Kind is used instead of a managed Kubernetes service to avoid paid resources.
- PostgreSQL runs inside Kubernetes for local demonstration.
- Secrets are demo values stored in raw YAML.
- No external secret manager.
- No production ingress controller installation is required for the local demo.
- No centralized logging stack.
- No Prometheus or Grafana.
- No autoscaling.
- No service mesh.

## What Would Break at Scale

- PostgreSQL is a single pod and can become a single point of failure.
- Local PVC storage is not a backup or disaster recovery strategy.
- NodePort access is fine for local Kind but not enterprise traffic routing.
- Worker polling works for a demo but would need queue semantics at scale.
- Manual `kubectl apply` can drift without GitOps controls.
- Demo secrets in Git are not acceptable for production.

## Production Improvements

- Use managed PostgreSQL with backups and high availability.
- Use Azure Key Vault, Vault, or External Secrets Operator.
- Add Prometheus, Grafana, and alerting.
- Add structured logging and trace correlation.
- Add HorizontalPodAutoscaler.
- Add PodDisruptionBudgets.
- Add NetworkPolicies.
- Use Argo CD or Flux for GitOps.
- Use canary or blue-green deployments.
- Add image scanning and SBOM generation.

## Reliability Probe Tradeoff

Readiness and liveness probes protect traffic and recovery behavior, but bad
configuration can create incidents:

- Too short timeout can mark healthy pods unhealthy.
- Too small initial delay can fail during normal startup.
- Too aggressive liveness probes can cause restart loops.
- Too strict readiness probes can stall deployments.

