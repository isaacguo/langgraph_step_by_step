"""
Error Handling - Basic Error Handling
Demonstrates basic error handling patterns in LangGraph
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()


class GraphState(TypedDict):
    messages: Annotated[list, "messages"]
    error: str
    status: str
    step_count: int


def try_except_pattern():
    """Try-except pattern in nodes"""
    print("=" * 60)
    print("Example 1: Try-Except Pattern")
    print("=" * 60)
    
    def risky_operation_node(state: GraphState):
        """Node that might fail"""
        try:
            # Simulate operation that might fail
            step = state.get("step_count", 0) + 1
            if step == 2:
                raise ValueError("Simulated error at step 2")
            
            return {
                "step_count": step,
                "status": "success",
                "error": ""
            }
        except Exception as e:
            return {
                "step_count": state.get("step_count", 0),
                "status": "error",
                "error": str(e)
            }
    
    def error_handler_node(state: GraphState):
        """Handle errors"""
        error = state.get("error", "")
        print(f"  Error handled: {error}")
        return {
            "status": "recovered",
            "error": ""
        }
    
    def route_by_status(state: GraphState) -> Literal["continue", "handle_error"]:
        """Route based on status"""
        if state.get("status") == "error":
            return "handle_error"
        return "continue"
    
    # Build graph
    workflow = StateGraph(GraphState)
    workflow.add_node("risky", risky_operation_node)
    workflow.add_node("error_handler", error_handler_node)
    
    workflow.set_entry_point("risky")
    workflow.add_conditional_edges(
        "risky",
        route_by_status,
        {
            "continue": END,
            "handle_error": "error_handler"
        }
    )
    workflow.add_edge("error_handler", END)
    
    app = workflow.compile()
    
    # Execute
    state = {"messages": [], "error": "", "status": "", "step_count": 0}
    
    for i in range(3):
        state = app.invoke(state)
        print(f"  Step {i+1}: status={state['status']}, step_count={state['step_count']}")
    
    print()


def error_propagation_example():
    """Error propagation through graph"""
    print("=" * 60)
    print("Example 2: Error Propagation")
    print("=" * 60)
    
    def node_a(state: GraphState):
        """Node A - might fail"""
        try:
            if state.get("step_count", 0) == 0:
                raise RuntimeError("Error in node A")
            return {"step_count": state.get("step_count", 0) + 1}
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def node_b(state: GraphState):
        """Node B - checks for errors"""
        if state.get("status") == "error":
            return {"status": "error_propagated"}
        return {"step_count": state.get("step_count", 0) + 1}
    
    def node_c(state: GraphState):
        """Node C - final handler"""
        if state.get("status") == "error_propagated":
            print(f"  Error propagated: {state.get('error', 'unknown')}")
            return {"status": "handled"}
        return state
    
    workflow = StateGraph(GraphState)
    workflow.add_node("a", node_a)
    workflow.add_node("b", node_b)
    workflow.add_node("c", node_c)
    
    workflow.set_entry_point("a")
    workflow.add_edge("a", "b")
    workflow.add_edge("b", "c")
    workflow.add_edge("c", END)
    
    app = workflow.compile()
    
    state = {"messages": [], "error": "", "status": "", "step_count": 0}
    result = app.invoke(state)
    
    print(f"Final status: {result['status']}")
    print()


def validation_example():
    """Input validation pattern"""
    print("=" * 60)
    print("Example 3: Input Validation")
    print("=" * 60)
    
    def validate_node(state: GraphState):
        """Validate input"""
        input_data = state.get("messages", [])
        
        if not input_data:
            return {
                "status": "validation_error",
                "error": "No input provided"
            }
        
        if len(input_data) > 10:
            return {
                "status": "validation_error",
                "error": "Input too large"
            }
        
        return {
            "status": "valid",
            "error": ""
        }
    
    def process_node(state: GraphState):
        """Process valid input"""
        return {
            "status": "processed",
            "step_count": state.get("step_count", 0) + 1
        }
    
    def route_decision(state: GraphState) -> Literal["process", "error"]:
        """Route based on validation"""
        if state.get("status") == "valid":
            return "process"
        return "error"
    
    workflow = StateGraph(GraphState)
    workflow.add_node("validate", validate_node)
    workflow.add_node("process", process_node)
    
    workflow.set_entry_point("validate")
    workflow.add_conditional_edges(
        "validate",
        route_decision,
        {
            "process": "process",
            "error": END
        }
    )
    workflow.add_edge("process", END)
    
    app = workflow.compile()
    
    # Test cases
    test_cases = [
        {"messages": ["valid input"], "error": "", "status": "", "step_count": 0},
        {"messages": [], "error": "", "status": "", "step_count": 0},
        {"messages": [f"msg_{i}" for i in range(15)], "error": "", "status": "", "step_count": 0}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}:")
        result = app.invoke(test_case)
        print(f"  Status: {result['status']}")
        if result.get("error"):
            print(f"  Error: {result['error']}")
    
    print()


if __name__ == "__main__":
    try:
        try_except_pattern()
        error_propagation_example()
        validation_example()
        
        print("=" * 60)
        print("All error handling examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

