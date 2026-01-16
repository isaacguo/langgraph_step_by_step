# Deployment Guide

## Environment Setup
1. **Rancher Desktop**: Ensure it is running with Kubernetes enabled (dockerd runtime).
2. **LM Studio**:
   - Load `qwen/qwen3-4b-2507`.
   - Start Server on port 1234.
   - Ensure "Cross-Origin Resource Sharing (CORS)" is enabled if accessing from browser (optional for this setup).

## Docker Build
The application is containerized using Docker.

```bash
cd project_14_k8s_deployment
docker build -t langgraph-safety:latest -f docker/Dockerfile .
```
*Note: We assume the image is available locally to the K8s cluster (Rancher Desktop does this automatically).*

## Kubernetes Deployment
We use standard K8s manifests.

1. **Create Namespace**
   ```bash
   kubectl apply -f k8s/namespace.yaml
   ```

2. **Deploy Configuration & Secrets**
   ```bash
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/secret.yaml
   ```

3. **Deploy Storage (PVC)**
   ```bash
   kubectl apply -f k8s/pvc/
   ```

4. **Deploy Database (Postgres)**
   ```bash
   kubectl apply -f k8s/postgresql/
   ```

5. **Deploy Application**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```

## Verification
1. Check Pod status:
   ```bash
   kubectl get pods -n langgraph-safety
   ```
2. Port forward to access locally (if NodePort is not reachable directly):
   ```bash
   kubectl port-forward svc/langgraph-service 8080:80 -n langgraph-safety
   ```
3. Test Health:
   ```bash
   curl http://localhost:8080/health
   ```
