#!/bin/bash
set -e

echo "Deploying Grafana..."
cd "$(dirname "$0")/.."

# Deploy Grafana resources
kubectl apply -f k8s/grafana/grafana-pvc.yaml
kubectl apply -f k8s/grafana/grafana-datasources.yaml
kubectl apply -f k8s/grafana/grafana-dashboard-provider.yaml
kubectl apply -f k8s/grafana/grafana-dashboard.yaml
kubectl apply -f k8s/grafana/deployment.yaml
kubectl apply -f k8s/grafana/service.yaml

echo "Grafana deployed. Access at http://localhost:30002"
echo "Default credentials: admin/admin"
echo "Wait for Grafana to be ready: kubectl get pods -n langgraph-safety -l app=grafana"
