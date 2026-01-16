# Project 4: Memory & Persistence

## Overview
This project covers different types of memory management and state persistence in LangGraph applications, including conversation memory types and checkpoint-based state persistence.

## Concepts Covered
- Conversation buffer memory
- Summary memory
- Window memory
- Checkpoint persistence
- State recovery
- Multiple thread management
- MemorySaver checkpointer

## Files
- `01_memory_types.py` - Different types of conversation memory
- `02_state_persistence.py` - Persisting and recovering state with checkpoints

## Running Examples

```bash
conda activate arxiv-paper
cd project_4_memory_persistence
python 01_memory_types.py
```

## Prerequisites
- Complete Projects 1-3
- Understanding of state management in LangGraph
- Knowledge of conversation context management

## Key Learning Points
- Choosing appropriate memory types for different use cases
- Implementing state persistence with checkpoints
- Recovering state after application restarts
- Managing multiple independent conversation threads
- Understanding memory trade-offs (buffer vs. summary vs. window)
