"""
Error Handling - Retry Mechanisms
Demonstrates retry patterns with exponential backoff
"""

import os
import time
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()


class GraphState(TypedDict):
    messages: Annotated[list, "messages"]
    attempt_count: int
    max_attempts: int
    status: str
    error: str


def simple_retry_pattern():
    """Simple retry pattern"""
    print("=" * 60)
    print("Example 1: Simple Retry Pattern")
    print("=" * 60)
    
    def operation_node(state: GraphState):
        """Operation that might fail"""
        attempt = state.get("attempt_count", 0) + 1
        max_attempts = state.get("max_attempts", 3)
        
        print(f"  Attempt {attempt}/{max_attempts}")
        
        # Simulate failure on first 2 attempts
        if attempt < 3:
            return {
                "attempt_count": attempt,
                "status": "retry",
                "error": f"Failed on attempt {attempt}"
            }
        
        return {
            "attempt_count": attempt,
            "status": "success",
            "error": ""
        }
    
    def route_decision(state: GraphState) -> Literal["retry", "success"]:
        """Route based on status"""
        if state.get("status") == "success":
            return "success"
        
        attempt = state.get("attempt_count", 0)
        max_attempts = state.get("max_attempts", 3)
        
        if attempt < max_attempts:
            return "retry"
        return "success"  # Give up after max attempts
    
    workflow = StateGraph(GraphState)
    workflow.add_node("operation", operation_node)
    
    workflow.set_entry_point("operation")
    workflow.add_conditional_edges(
        "operation",
        route_decision,
        {
            "retry": "operation",
            "success": END
        }
    )
    
    app = workflow.compile()
    
    state = {
        "messages": [],
        "attempt_count": 0,
        "max_attempts": 3,
        "status": "",
        "error": ""
    }
    
    result = app.invoke(state)
    print(f"\nFinal status: {result['status']}")
    print(f"Total attempts: {result['attempt_count']}")
    print()


def exponential_backoff_retry():
    """Retry with exponential backoff"""
    print("=" * 60)
    print("Example 2: Exponential Backoff Retry")
    print("=" * 60)
    
    def operation_with_backoff(state: GraphState):
        """Operation with backoff"""
        attempt = state.get("attempt_count", 0) + 1
        backoff_time = min(2 ** attempt, 8)  # Cap at 8 seconds
        
        print(f"  Attempt {attempt}, backoff: {backoff_time}s")
        
        if attempt < 3:
            time.sleep(backoff_time)  # Simulate backoff
            return {
                "attempt_count": attempt,
                "status": "retry",
                "error": f"Failed, waiting {backoff_time}s"
            }
        
        return {
            "attempt_count": attempt,
            "status": "success"
        }
    
    def route_decision(state: GraphState) -> Literal["retry", "success"]:
        """Route decision"""
        if state.get("status") == "success":
            return "success"
        
        if state.get("attempt_count", 0) < 3:
            return "retry"
        return "success"
    
    workflow = StateGraph(GraphState)
    workflow.add_node("operation", operation_with_backoff)
    
    workflow.set_entry_point("operation")
    workflow.add_conditional_edges(
        "operation",
        route_decision,
        {
            "retry": "operation",
            "success": END
        }
    )
    
    app = workflow.compile()
    
    state = {
        "messages": [],
        "attempt_count": 0,
        "max_attempts": 3,
        "status": "",
        "error": ""
    }
    
    print("Executing with exponential backoff...")
    result = app.invoke(state)
    print(f"\nFinal status: {result['status']}")
    print(f"Total attempts: {result['attempt_count']}")
    print()


if __name__ == "__main__":
    try:
        simple_retry_pattern()
        exponential_backoff_retry()
        
        print("=" * 60)
        print("All retry mechanism examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

