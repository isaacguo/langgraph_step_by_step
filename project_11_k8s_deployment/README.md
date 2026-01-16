# Agentic Runtime Safety & Stability System

## Overview
This project implements a production-ready runtime safety system for agentic AI applications. It is designed to be deployed on Kubernetes and integrates with local LLMs via LM Studio.

## Key Features
- **Runtime Guardrails**: Role-based authorization and policy enforcement.
- **Intent Safety**: LLM-based intent parsing and prompt injection detection.
- **Safety Contracts**: Formal definition and validation of operation boundaries.
- **Fault Isolation**: Process-based sandboxing and error containment.
- **Observability**: Structured logging, distributed tracing, and Prometheus metrics.
- **Self-Healing**: Automatic rollback to safe checkpoints upon violation.
- **Adaptive Governance**: Dynamic policy adjustment based on feedback.

## Architecture
The system follows a modular architecture:
- **FastAPI**: Serves the REST API.
- **LangGraph**: Orchestrates the agent workflow.
- **Safety Modules**: Intercept and validate all actions.
- **PostgreSQL**: Stores state and checkpoints.
- **LM Studio**: Provides local LLM inference.

## Quick Start

### Prerequisites
- Docker & Kubernetes (Rancher Desktop recommended)
- LM Studio (running locally on port 1234)

### Build & Deploy
```bash
# Build Docker image
docker build -t langgraph-safety:latest -f docker/Dockerfile .

# Apply K8s manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/
```

### Usage
Send a chat request:
```bash
curl -X POST http://localhost:30000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user1", "content": "Hello, can you help me?"}'
```

See `docs/` for detailed documentation.
