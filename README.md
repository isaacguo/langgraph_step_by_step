# LangChain & LangGraph Tutorial Series

A comprehensive, systematic learning path for LangChain and LangGraph covering fundamental concepts to advanced patterns.

## Tutorial Structure

This series is organized into 8 progressive projects:

1. **Project 1: LangChain Basics** - Chains, prompts, LLMs, and basic workflows
2. **Project 2: LangGraph Basics** - State graphs, nodes, edges, and control flow
3. **Project 3: Agent Communication Patterns** - Multi-agent systems and communication architectures
4. **Project 4: Memory Management & State Persistence** - Conversation memory, state storage, and retrieval
5. **Project 5: Error Handling & Failure Recovery** - Robust error handling, retries, and recovery strategies
6. **Project 6: Scalability & Resource Management** - Parallel processing, batching, and optimization
7. **Project 7: Observability & Debugging** - Logging, tracing, monitoring, and debugging tools
8. **Project 8: Agentic Runtime Safety & Observability** - Production-grade safety, stability, and observability for agentic systems

## Setup

### Prerequisites
- Python 3.10 or higher
- Conda (Miniconda or Anaconda)

### Environment Setup

```bash
# Create conda environment
conda create -n langgraph_exec python=3.10 -y
conda activate langgraph_exec

# Install base dependencies
pip install langchain langchain-openai langgraph langchain-community python-dotenv requests

# Setup LM Studio (required for running examples)
# 1. Download and install LM Studio from https://lmstudio.ai/
# 2. Load the model: qwen/qwen3-4b-2507
# 3. Start the local server on port 1234
# 4. Make sure the server is running before executing examples
```

### Running Tutorials

Each project is self-contained with its own directory:
- Navigate to the project directory
- Follow the project-specific README
- Run the examples as shown

## Learning Path

Work through projects sequentially as each builds upon previous concepts. Each project includes:
- Clear explanations of concepts
- Working code examples
- Exercises and challenges
- Best practices and patterns

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Cookbook](https://github.com/langchain-ai/langchain-cookbook)

