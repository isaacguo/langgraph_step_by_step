"""
ReAct Agent - Basic Example
Demonstrates how to create and use a ReAct (Reasoning + Acting) agent with multiple tools
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import tool

# Add utils to path for utility function
_file_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_file_dir, '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from utils.llm_config import get_local_llm

# Load environment variables
load_dotenv()


@tool
def calculator(expression: str) -> str:
    """Evaluates a mathematical expression. Input should be a valid Python mathematical expression."""
    try:
        # Safe evaluation - only allow basic math operations
        allowed_chars = set('0123456789+-*/()., ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression. Only basic math operations are allowed."
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"


@tool
def search_tool(query: str) -> str:
    """Searches for information about a given topic. Returns simulated search results."""
    # Simulated search results - in a real scenario, this would call an actual search API
    search_results = {
        "python": "Python is a high-level programming language known for its simplicity and readability.",
        "ai": "Artificial Intelligence (AI) is the simulation of human intelligence by machines.",
        "langchain": "LangChain is a framework for developing applications powered by language models.",
        "machine learning": "Machine learning is a subset of AI that enables systems to learn from data.",
    }
    
    query_lower = query.lower()
    for key, value in search_results.items():
        if key in query_lower:
            return f"Search results for '{query}': {value}"
    
    return f"Search results for '{query}': Information not found in knowledge base. This is a simulated search tool."


@tool
def file_operations(operation: str, filename: Optional[str] = None, content: Optional[str] = None) -> str:
    """Performs file operations: 'read', 'write', or 'list'. 
    For 'write', provide filename and content. For 'read', provide filename. For 'list', no filename needed."""
    try:
        if operation == "list":
            # List files in current directory
            files = [f for f in os.listdir('.') if os.path.isfile(f)]
            return f"Files in current directory: {', '.join(files[:10])}"  # Limit to first 10
        elif operation == "read":
            if not filename:
                return "Error: filename is required for read operation"
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    return f"File '{filename}' content (first 500 chars): {content[:500]}"
            else:
                return f"Error: File '{filename}' not found"
        elif operation == "write":
            if not filename or content is None:
                return "Error: filename and content are required for write operation"
            # Create a safe directory for demo files
            demo_dir = "demo_files"
            os.makedirs(demo_dir, exist_ok=True)
            filepath = os.path.join(demo_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote {len(content)} characters to '{filepath}'"
        else:
            return f"Error: Unknown operation '{operation}'. Use 'read', 'write', or 'list'"
    except Exception as e:
        return f"Error in file operation: {str(e)}"


@tool
def time_tool(timezone: Optional[str] = None) -> str:
    """Gets the current date and time. Optional timezone parameter (default: local time)."""
    now = datetime.now()
    if timezone:
        return f"Current time in {timezone}: {now.strftime('%Y-%m-%d %H:%M:%S')} (Note: timezone conversion not implemented in demo)"
    return f"Current local time: {now.strftime('%Y-%m-%d %H:%M:%S')}"


def basic_react_agent_example():
    """Basic ReAct agent with multiple tools"""
    print("=" * 60)
    print("Example 1: Basic ReAct Agent with Multiple Tools")
    print("=" * 60)
    
    # Get the ReAct prompt template from LangChain Hub
    print("\nLoading ReAct prompt template from LangChain Hub...")
    try:
        prompt = hub.pull("hwchase17/react")
        print("✓ Prompt template loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load prompt from hub: {e}")
        print("Using default ReAct prompt structure...")
        from langchain_core.prompts import PromptTemplate
        prompt = PromptTemplate.from_template(
            "You are a helpful assistant that can use tools to answer questions.\n\n"
            "You have access to the following tools:\n{tools}\n\n"
            "Use the following format:\n\n"
            "Question: the input question you must answer\n"
            "Thought: you should always think about what to do\n"
            "Action: the action to take, should be one of [{tool_names}]\n"
            "Action Input: the input to the action\n"
            "Observation: the result of the action\n"
            "... (this Thought/Action/Action Input/Observation can repeat N times)\n"
            "Thought: I now know the final answer\n"
            "Final Answer: the final answer to the original input question\n\n"
            "Question: {input}\n"
            "Thought: {agent_scratchpad}"
        )
    
    # Get local LLM
    llm = get_local_llm(temperature=0.7)
    
    # Define tools
    tools = [calculator, search_tool, file_operations, time_tool]
    
    print(f"\nAvailable tools: {[tool.name for tool in tools]}")
    
    # Create the ReAct agent
    print("\nCreating ReAct agent...")
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )
    
    # Test scenarios
    test_queries = [
        "What is 25 * 4 + 10?",
        "What is the current time?",
        "Search for information about Python",
        "Calculate (100 + 50) / 3 and then search for information about AI"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {query}")
        print('='*60)
        try:
            result = agent_executor.invoke({"input": query})
            print(f"\n✓ Result: {result.get('output', 'No output')}")
        except Exception as e:
            print(f"\n✗ Error: {e}")
        print()


def complex_task_example():
    """Complex task requiring multiple tool uses"""
    print("=" * 60)
    print("Example 2: Complex Task with Multiple Tool Interactions")
    print("=" * 60)
    
    # Get prompt
    try:
        prompt = hub.pull("hwchase17/react")
    except Exception:
        from langchain_core.prompts import PromptTemplate
        prompt = PromptTemplate.from_template(
            "You are a helpful assistant that can use tools to answer questions.\n\n"
            "You have access to the following tools:\n{tools}\n\n"
            "Use the following format:\n\n"
            "Question: the input question you must answer\n"
            "Thought: you should always think about what to do\n"
            "Action: the action to take, should be one of [{tool_names}]\n"
            "Action Input: the input to the action\n"
            "Observation: the result of the action\n"
            "... (this Thought/Action/Action Input/Observation can repeat N times)\n"
            "Thought: I now know the final answer\n"
            "Final Answer: the final answer to the original input question\n\n"
            "Question: {input}\n"
            "Thought: {agent_scratchpad}"
        )
    
    llm = get_local_llm(temperature=0.7)
    tools = [calculator, search_tool, file_operations, time_tool]
    
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10
    )
    
    complex_query = (
        "First, calculate what 15 * 8 equals. "
        "Then, write that result to a file called 'result.txt'. "
        "Finally, read the file back and tell me what's in it."
    )
    
    print(f"\nComplex Query: {complex_query}\n")
    try:
        result = agent_executor.invoke({"input": complex_query})
        print(f"\n✓ Final Result: {result.get('output', 'No output')}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    print()


def interactive_example():
    """Interactive example where user can ask questions"""
    print("=" * 60)
    print("Example 3: Interactive ReAct Agent")
    print("=" * 60)
    print("You can ask questions and the agent will use tools to answer them.")
    print("Type 'exit' to quit.\n")
    
    try:
        prompt = hub.pull("hwchase17/react")
    except Exception:
        from langchain_core.prompts import PromptTemplate
        prompt = PromptTemplate.from_template(
            "You are a helpful assistant that can use tools to answer questions.\n\n"
            "You have access to the following tools:\n{tools}\n\n"
            "Use the following format:\n\n"
            "Question: the input question you must answer\n"
            "Thought: you should always think about what to do\n"
            "Action: the action to take, should be one of [{tool_names}]\n"
            "Action Input: the input to the action\n"
            "Observation: the result of the action\n"
            "... (this Thought/Action/Action Input/Observation can repeat N times)\n"
            "Thought: I now know the final answer\n"
            "Final Answer: the final answer to the original input question\n\n"
            "Question: {input}\n"
            "Thought: {agent_scratchpad}"
        )
    
    llm = get_local_llm(temperature=0.7)
    tools = [calculator, search_tool, file_operations, time_tool]
    
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10
    )
    
    print("Available tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            print()
            result = agent_executor.invoke({"input": user_input})
            print(f"\nAgent: {result.get('output', 'No response')}\n")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    # Check for LM Studio server
    import requests
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=2)
        if response.status_code != 200:
            print("WARNING: LM Studio server may not be running on port 1234")
    except requests.exceptions.RequestException:
        print("WARNING: Cannot connect to LM Studio server at http://localhost:1234")
        print("Make sure LM Studio is running and the server is started.")
        print()
    
    try:
        basic_react_agent_example()
        complex_task_example()
        
        # Uncomment to run interactive example
        # interactive_example()
        
        print("=" * 60)
        print("All ReAct agent examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
