# Failure Scenario

Issue:
Backend unable to connect to PostgreSQL.

Symptoms:
- Pod CrashLoopBackOff
- Health checks failing

Debug Commands:
kubectl get pods
kubectl describe pod
kubectl logs
kubectl get svc

Fix:
Correct DB host service name.
