#!/bin/bash
set -e

echo "Deploying to Kubernetes..."
cd "$(dirname "$0")/.."

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/pvc/
kubectl apply -f k8s/postgresql/
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/serviceaccount.yaml

echo "Deployment initiated. Check status with: kubectl get pods -n langgraph-safety"
