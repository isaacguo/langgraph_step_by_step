"""
Observability - Tracing
Demonstrates execution tracing for debugging
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()


class GraphState(TypedDict):
    messages: Annotated[list, "messages"]
    trace: Annotated[list, "execution trace"]
    step_count: int


def execution_tracing_example():
    """Trace execution flow"""
    print("=" * 60)
    print("Example 1: Execution Tracing")
    print("=" * 60)
    
    def traced_node_a(state: GraphState):
        """Node A with tracing"""
        trace = state.get("trace", [])
        trace.append("node_a")
        
        return {
            "trace": trace,
            "step_count": state.get("step_count", 0) + 1
        }
    
    def traced_node_b(state: GraphState):
        """Node B with tracing"""
        trace = state.get("trace", [])
        trace.append("node_b")
        
        return {
            "trace": trace,
            "step_count": state["step_count"] + 1
        }
    
    def traced_node_c(state: GraphState):
        """Node C with tracing"""
        trace = state.get("trace", [])
        trace.append("node_c")
        
        return {
            "trace": trace,
            "step_count": state["step_count"] + 1
        }
    
    workflow = StateGraph(GraphState)
    workflow.add_node("a", traced_node_a)
    workflow.add_node("b", traced_node_b)
    workflow.add_node("c", traced_node_c)
    
    workflow.set_entry_point("a")
    workflow.add_edge("a", "b")
    workflow.add_edge("b", "c")
    workflow.add_edge("c", END)
    
    app = workflow.compile()
    
    state = {"messages": [], "trace": [], "step_count": 0}
    result = app.invoke(state)
    
    print("Execution trace:")
    for i, node in enumerate(result["trace"], 1):
        print(f"  {i}. {node}")
    print()


def state_tracing_example():
    """Trace state changes"""
    print("=" * 60)
    print("Example 2: State Tracing")
    print("=" * 60)
    
    def state_traced_node(state: GraphState):
        """Node that traces state changes"""
        trace = state.get("trace", [])
        previous_step = state.get("step_count", 0)
        current_step = previous_step + 1
        
        trace.append({
            "node": "state_traced",
            "previous_step": previous_step,
            "current_step": current_step,
            "state_keys": list(state.keys())
        })
        
        return {
            "trace": trace,
            "step_count": current_step
        }
    
    workflow = StateGraph(GraphState)
    workflow.add_node("traced", state_traced_node)
    workflow.set_entry_point("traced")
    workflow.add_edge("traced", END)
    
    app = workflow.compile()
    
    state = {"messages": [], "trace": [], "step_count": 0}
    result = app.invoke(state)
    
    print("State trace:")
    for entry in result["trace"]:
        print(f"  Node: {entry['node']}")
        print(f"    Step: {entry['previous_step']} -> {entry['current_step']}")
        print(f"    State keys: {entry['state_keys']}")
    print()


if __name__ == "__main__":
    try:
        execution_tracing_example()
        state_tracing_example()
        
        print("=" * 60)
        print("All tracing examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

