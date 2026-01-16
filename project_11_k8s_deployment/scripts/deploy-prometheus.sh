#!/bin/bash
set -e

echo "Deploying Prometheus..."
cd "$(dirname "$0")/.."

# Deploy RBAC resources first
kubectl apply -f k8s/prometheus/serviceaccount.yaml
kubectl apply -f k8s/prometheus/clusterrole.yaml
kubectl apply -f k8s/prometheus/clusterrolebinding.yaml

# Deploy Prometheus resources
kubectl apply -f k8s/prometheus/prometheus-pvc.yaml
kubectl apply -f k8s/prometheus/prometheus-config.yaml
kubectl apply -f k8s/prometheus/deployment.yaml
kubectl apply -f k8s/prometheus/service.yaml

echo "Prometheus deployed. Access at http://localhost:30001"
echo "Wait for Prometheus to be ready: kubectl get pods -n langgraph-safety -l app=prometheus"
echo "Check targets at: http://localhost:30001/targets"