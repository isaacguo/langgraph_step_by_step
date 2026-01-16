# System Architecture

## Overview
The system is built on the **Agentic Runtime Safety** pattern, ensuring that autonomous agents operate within defined boundaries.

## Components

### 1. Safety Orchestrator
The central coordinator that invokes validation steps before and after agent execution.

### 2. Runtime Guardrails
- **Authorization**: Checks user permissions using RBAC.
- **Policy Enforcement**: Blocks prohibited actions (e.g., SQL injection, shell execution).

### 3. Intent Safety
- **Parser**: Extracts structured intent from natural language using LLM.
- **Prompt Safety**: Detects jailbreak attempts and injection attacks.

### 4. Recovery & Isolation
- **Checkpointing**: Persists state to Postgres after every step.
- **Sandboxing**: Executes risky code in isolated processes with resource limits.

### 5. Observability
- **Telemetry**: Logs all decisions and traces.
- **Metrics**: Exposes Prometheus metrics for monitoring safety score and violations.

## Data Flow
1. User Request -> API -> Orchestrator
2. Orchestrator -> Guardrails (Auth Check)
3. Orchestrator -> Intent Safety (Parsing)
4. Orchestrator -> LangGraph (Execution)
   - Node Execution -> Safety Check -> Process -> Result
5. Result -> API -> User
