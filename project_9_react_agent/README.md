# Project 9: ReAct Agent

## Overview
This project demonstrates how to create and use ReAct (Reasoning + Acting) agents with LangChain. ReAct agents combine reasoning and acting capabilities, allowing them to use tools to answer questions and complete tasks.

## Concepts Covered
- ReAct agent architecture
- Tool definition and usage
- Agent execution with multiple tools
- Complex task decomposition
- Interactive agent systems
- Tool chaining and orchestration

## Files
- `01_react_agent_basic.py` - Basic ReAct agent with multiple tools (calculator, search, file operations, time)

## Running Examples

```bash
conda activate arxiv-paper
cd project_9_react_agent
python 01_react_agent_basic.py
```

## Prerequisites
- Complete Projects 1-4
- Understanding of agent architectures
- Knowledge of tool usage in LangChain

## Key Learning Points
- Creating ReAct agents with LangChain
- Defining and using custom tools
- Understanding the ReAct loop (Reasoning → Acting → Observing)
- Handling complex tasks that require multiple tool uses
- Building interactive agent systems
- Managing tool execution and error handling

## Available Tools in Examples
- **Calculator**: Evaluates mathematical expressions
- **Search Tool**: Simulated search functionality
- **File Operations**: Read, write, and list files
- **Time Tool**: Get current date and time
