# Project 1: LangChain Basics

## Overview
This project introduces the fundamental concepts of LangChain, including prompts, LLMs, chains, output parsers, and basic memory management. These are the building blocks for more advanced LangGraph applications.

## Concepts Covered
- Prompt templates (PromptTemplate and ChatPromptTemplate)
- LLM interactions and streaming
- Simple chains (LLMChain)
- Sequential chains
- Output parsers
- Basic memory types (Buffer, Summary, Window)

## Files
- `01_prompts_and_llms.py` - Basic prompt templates and LLM calls
- `02_simple_chains.py` - Creating and using simple chains
- `03_sequential_chains.py` - Chaining multiple operations together
- `04_output_parsers.py` - Parsing and structuring LLM outputs
- `05_basic_memory.py` - Introduction to conversation memory

## Running Examples

```bash
conda activate arxiv-paper
cd project_1_langchain_basics
python 01_prompts_and_llms.py
```

## Prerequisites
- Python 3.8+
- LangChain and LangChain Core installed
- LM Studio running on localhost:1234 (or configure your LLM endpoint)
- Environment variables configured (see `.env` file)

## Key Learning Points
- Understanding how to structure prompts for LLMs
- Creating reusable chains for common operations
- Managing conversation context with memory
- Parsing structured outputs from LLM responses
