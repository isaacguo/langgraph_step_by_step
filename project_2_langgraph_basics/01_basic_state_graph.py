"""
LangGraph Basics - Basic State Graph
Demonstrates creating a simple state graph with nodes and edges
"""

import os
import sys
import operator
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate

# Add utils to path for utility function
_file_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_file_dir, '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from utils.llm_config import get_local_llm

# Load environment variables
load_dotenv()

# Define state schema
class GraphState(TypedDict):
    messages: Annotated[list, "list of messages"]
    step_count: int
    user_input: Annotated[str, "user input message"]


def create_basic_graph():
    """Create a simple linear graph"""
    print("=" * 60)
    print("Example 1: Basic Linear State Graph")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.7)
    
    # Define nodes
    def start_node(state: GraphState):
        """Initial node that starts the conversation"""
        print("Executing: start_node")
        return {
            "messages": [{"role": "system", "content": "You are a helpful assistant."}],
            "step_count": 1,
            "user_input": state.get("user_input", "")  # Preserve user_input in state
        }
    
    def process_node(state: GraphState):
        """Process the input"""
        print("Executing: process_node")
        user_input = state.get("user_input", "Hello")
        
        prompt = ChatPromptTemplate.from_template(
            "Respond to this message: {message}"
        )
        chain = prompt | llm
        
        response = chain.invoke({"message": user_input})
        
        return {
            "messages": state["messages"] + [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": response.content}
            ],
            "step_count": state["step_count"] + 1
        }
    
    def end_node(state: GraphState):
        """Final node"""
        print("Executing: end_node")
        return {
            "step_count": state["step_count"] + 1
        }
    
    # Build graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("start", start_node)
    workflow.add_node("process", process_node)
    workflow.add_node("end", end_node)
    
    # Add edges
    workflow.set_entry_point("start")
    workflow.add_edge("start", "process")
    workflow.add_edge("process", "end")
    workflow.add_edge("end", END)
    
    # Compile graph
    app = workflow.compile()
    
    # Execute with strongly-typed initial state
    initial_state: GraphState = {
        "messages": [],
        "step_count": 0,
        "user_input": "What is Python?"
    }
    result = app.invoke(initial_state)
    
    print("\nFinal State:")
    print(f"Step count: {result['step_count']}")
    print(f"Messages: {len(result['messages'])}")
    for msg in result["messages"]:
        if isinstance(msg, dict):
            print(f"  {msg.get('role', 'unknown')}: {msg.get('content', '')[:100]}")
    print()


def create_branching_graph():
    """Create a graph with branching paths based on input length"""
    print("=" * 60)
    print("Example 2: Branching Graph")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.7)
    
    def input_node(state: GraphState):
        """Get user input"""
        print("Executing: input_node")
        return {
            "messages": state.get("messages", []),
            "step_count": state.get("step_count", 0) + 1,
            "user_input": state.get("user_input", "")
        }
    
    def analyze_node(state: GraphState):
        """Analyze the input"""
        print("Executing: analyze_node")
        user_input = state.get("user_input", "")
        
        prompt = ChatPromptTemplate.from_template(
            "Analyze this text and provide insights: {text}"
        )
        chain = prompt | llm
        response = chain.invoke({"text": user_input})
        
        return {
            "messages": state["messages"] + [
                {"role": "assistant", "content": f"Analysis: {response.content}"}
            ],
            "step_count": state["step_count"] + 1,
            "user_input": user_input
        }
    
    def detail_node(state: GraphState):
        """Provide detailed analysis for longer inputs"""
        print("Executing: detail_node (Detailed Analysis Path)")
        user_input = state.get("user_input", "")
        
        prompt = ChatPromptTemplate.from_template(
            "Provide a detailed, in-depth analysis of: {text}"
        )
        chain = prompt | llm
        response = chain.invoke({"text": user_input})
        
        return {
            "messages": state["messages"] + [
                {"role": "assistant", "content": f"Detailed Analysis: {response.content}"}
            ],
            "step_count": state["step_count"] + 1,
            "user_input": user_input
        }
    
    def summarize_node(state: GraphState):
        """Summarize the conversation"""
        print("Executing: summarize_node")
        messages_text = "\n".join([
            msg.get("content", "") for msg in state["messages"] 
            if isinstance(msg, dict)
        ])
        
        prompt = ChatPromptTemplate.from_template(
            "Summarize this conversation: {conversation}"
        )
        chain = prompt | llm
        response = chain.invoke({"conversation": messages_text})
        
        return {
            "messages": state["messages"] + [
                {"role": "assistant", "content": f"Summary: {response.content}"}
            ],
            "step_count": state["step_count"] + 1,
            "user_input": state.get("user_input", "")
        }
    
    def route_decision(state: GraphState) -> Literal["summarize", "detail"]:
        """Route based on input length - longer inputs get detailed analysis"""
        user_input = state.get("user_input", "")
        if len(user_input) > 30:
            print(f"  → Routing to DETAIL path (input length: {len(user_input)})")
            return "detail"
        else:
            print(f"  → Routing to SUMMARIZE path (input length: {len(user_input)})")
            return "summarize"
    
    # Build graph with branching
    workflow = StateGraph(GraphState)
    
    workflow.add_node("input", input_node)
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("detail", detail_node)
    workflow.add_node("summarize", summarize_node)
    
    workflow.set_entry_point("input")
    workflow.add_edge("input", "analyze")
    # Add conditional edge: after analyze, decide whether to summarize or go to detail
    workflow.add_conditional_edges(
        "analyze",
        route_decision,
        {
            "summarize": "summarize",  # Short input: go directly to summarize
            "detail": "detail"         # Long input: go to detail first
        }
    )
    workflow.add_edge("detail", "summarize")  # After detail, always summarize
    workflow.add_edge("summarize", END)
    
    app = workflow.compile()
    
    # Test with different inputs to show branching
    test_cases = [
        {
            "messages": [],
            "step_count": 0,
            "user_input": "Short text"  # Will take analyze -> summarize path
        },
        {
            "messages": [],
            "step_count": 0,
            "user_input": "This is a much longer input that will trigger the detailed analysis path"  # Will take analyze -> detail -> summarize path
        }
    ]
    
    for i, initial_state in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: '{initial_state['user_input']}' ---")
        result = app.invoke(initial_state)
        print(f"\nFinal State:")
        print(f"Step count: {result['step_count']}")
        print(f"Total messages: {len(result['messages'])}")
        for msg in result["messages"]:
            if isinstance(msg, dict):
                content = msg.get('content', '')
                role = msg.get('role', 'unknown')
                print(f"  {role}: {content[:80]}{'...' if len(content) > 80 else ''}")
    print()


def create_parallel_nodes():
    """Graph with true parallel execution (fan-out/fan-in pattern)"""
    print("=" * 60)
    print("Example 3: Parallel Node Execution")
    print("=" * 60)
    
    import time
    
    # Define a separate state schema for parallel execution
    # Use operator.add for messages to allow parallel nodes to merge their results
    class ParallelState(TypedDict):
        messages: Annotated[list, operator.add]  # Use operator.add to merge lists from parallel nodes
        step_count: int
        user_input: Annotated[str, "user input message"]
        node_a_result: Annotated[str, "result from node A"]
        node_b_result: Annotated[str, "result from node B"]
    
    def start_node(state: ParallelState):
        """Start node that triggers parallel execution"""
        print("Executing: start_node")
        return {
            "messages": [],
            "step_count": state.get("step_count", 0) + 1,
            "user_input": state.get("user_input", ""),
            "node_a_result": "",
            "node_b_result": ""
        }
    
    def node_a(state: ParallelState):
        """Node A - runs in parallel with node_b"""
        print("Executing: node_a (parallel)")
        time.sleep(0.1)  # Simulate work to demonstrate parallelism
        return {
            "messages": [{"role": "system", "content": "Node A executed"}],
            "node_a_result": "Result from Node A"
        }
    
    def node_b(state: ParallelState):
        """Node B - runs in parallel with node_a"""
        print("Executing: node_b (parallel)")
        time.sleep(0.1)  # Simulate work to demonstrate parallelism
        return {
            "messages": [{"role": "system", "content": "Node B executed"}],
            "node_b_result": "Result from Node B"
        }
    
    def merge_node(state: ParallelState):
        """Merge results from parallel nodes (fan-in)"""
        print("Executing: merge_node (collecting parallel results)")
        return {
            "messages": [{"role": "system", "content": f"Merged: {state.get('node_a_result', '')} + {state.get('node_b_result', '')}"}],
            "step_count": state.get("step_count", 0) + 1
        }
    
    # Build graph with parallel execution (fan-out/fan-in pattern)
    workflow = StateGraph(ParallelState)
    
    workflow.add_node("start", start_node)
    workflow.add_node("node_a", node_a)
    workflow.add_node("node_b", node_b)
    workflow.add_node("merge", merge_node)
    
    workflow.set_entry_point("start")
    # Fan-out: Both node_a and node_b start from "start" - enables parallel execution
    workflow.add_edge("start", "node_a")
    workflow.add_edge("start", "node_b")
    # Fan-in: Both nodes feed into merge
    workflow.add_edge("node_a", "merge")
    workflow.add_edge("node_b", "merge")
    workflow.add_edge("merge", END)
    
    app = workflow.compile()
    
    # Execute with strongly-typed initial state
    initial_state: ParallelState = {
        "messages": [],
        "step_count": 0,
        "user_input": "",
        "node_a_result": "",
        "node_b_result": ""
    }
    
    print("\nExecuting parallel workflow:")
    print("  start → [node_a, node_b] (parallel) → merge")
    print("  Note: node_a and node_b execute concurrently")
    result = app.invoke(initial_state)
    
    print("\nFinal State:")
    print(f"Step count: {result['step_count']}")
    print(f"Messages: {[msg.get('content', '') for msg in result['messages']]}")
    print(f"Node A result: {result.get('node_a_result', '')}")
    print(f"Node B result: {result.get('node_b_result', '')}")
    print("\n✓ Parallel execution demonstrated: both nodes executed concurrently")
    print("  and their results were merged using operator.add for messages.")
    print()


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
    
    try:
        create_basic_graph()
        create_branching_graph()
        create_parallel_nodes()
        
        print("=" * 60)
        print("All basic state graph examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

