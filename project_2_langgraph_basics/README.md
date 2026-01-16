# Project 2: LangGraph Basics

## Overview
This project covers the core concepts of LangGraph, including state graphs, conditional edges, state schemas, human-in-the-loop patterns, graph visualization, and common workflow patterns.

## Concepts Covered
- State graphs and nodes
- Conditional edges and routing
- State schemas (TypedDict)
- Human-in-the-loop workflows
- Graph visualization
- Common workflow patterns (pipeline, fan-out/fan-in, retry, state machine, error handling)

## Files
- `01_basic_state_graph.py` - Creating basic state graphs with nodes and edges
- `02_conditional_edges.py` - Using conditional logic to route between nodes
- `03_state_schemas.py` - Defining and using typed state schemas
- `04_human_in_loop.py` - Integrating human feedback into workflows
- `05_graph_visualization.py` - Visualizing graph structures
- `06_workflow_patterns.py` - Common workflow patterns and best practices

## Running Examples

```bash
conda activate arxiv-paper
cd project_2_langgraph_basics
python 01_basic_state_graph.py
```

## Prerequisites
- Complete Project 1 (LangChain Basics)
- Understanding of Python TypedDict
- Basic knowledge of graph structures

## Key Learning Points
- Building stateful workflows with LangGraph
- Implementing conditional routing logic
- Managing state across multiple nodes
- Creating reusable workflow patterns
- Integrating human feedback mechanisms
