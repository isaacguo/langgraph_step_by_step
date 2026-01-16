# Project 10: LangGraph Demo System

## Overview
This project provides a comprehensive demonstration system showcasing the full capabilities of LangGraph. It integrates multiple concepts including state management, conditional routing, parallel execution, error handling, and result aggregation into a complete working system.

## Concepts Covered
- Task classification and routing
- Multiple processing nodes (research, calculation, writing, analysis)
- Parallel node execution
- Conditional routing based on task type
- Error handling and recovery
- Result aggregation
- Interactive demo mode
- LLM integration for intelligent processing

## Files
- `01_demo_system.py` - Comprehensive demo system with multiple processing nodes
- `01_demo_system.ipynb` - Jupyter notebook version of the demo

## Running Examples

```bash
conda activate arxiv-paper
cd project_10_langgraph_demo
python 01_demo_system.py
```

Or use the Jupyter notebook:
```bash
jupyter notebook 01_demo_system.ipynb
```

## Prerequisites
- Complete Projects 1-9
- Understanding of all previous concepts
- LM Studio running on localhost:1234 (or configure your LLM endpoint)

## Key Learning Points
- Building a complete, integrated LangGraph system
- Combining multiple patterns (routing, parallel execution, error handling)
- Creating intelligent task classification
- Implementing multiple specialized processing nodes
- Aggregating results from parallel operations
- Building interactive demo systems

## System Features
- **Task Classification**: Automatically classifies tasks into different types (research, calculation, writing, analysis)
- **Parallel Processing**: Executes multiple processing nodes concurrently
- **Error Handling**: Gracefully handles errors and provides recovery mechanisms
- **Result Aggregation**: Combines results from multiple nodes into a final output
- **Interactive Mode**: Supports interactive task processing
