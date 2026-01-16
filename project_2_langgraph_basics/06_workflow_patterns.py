"""
LangGraph Basics - Common Workflow Patterns
Demonstrates common workflow patterns and best practices
"""

import os
import sys
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate

# Add utils to path for utility function (if needed)
_file_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_file_dir, '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from utils.llm_config import get_local_llm

# Load environment variables
load_dotenv()


class GraphState(TypedDict):
    messages: Annotated[list, "list of messages"]
    data: dict
    step_count: int
    status: str


def pipeline_pattern():
    """Linear pipeline pattern - sequential processing"""
    print("=" * 60)
    print("Example 1: Pipeline Pattern")
    print("=" * 60)
    
    def extract_node(state: GraphState):
        """Extract data"""
        print("  [Extract] Extracting data...")
        return {
            "data": {"raw": "Sample data"},
            "step_count": state.get("step_count", 0) + 1
        }
    
    def transform_node(state: GraphState):
        """Transform data"""
        print("  [Transform] Transforming data...")
        return {
            "data": {**state["data"], "transformed": True},
            "step_count": state["step_count"] + 1
        }
    
    def load_node(state: GraphState):
        """Load data"""
        print("  [Load] Loading data...")
        return {
            "data": {**state["data"], "loaded": True},
            "step_count": state["step_count"] + 1,
            "status": "completed"
        }
    
    workflow = StateGraph(GraphState)
    workflow.add_node("extract", extract_node)
    workflow.add_node("transform", transform_node)
    workflow.add_node("load", load_node)
    
    workflow.set_entry_point("extract")
    workflow.add_edge("extract", "transform")
    workflow.add_edge("transform", "load")
    workflow.add_edge("load", END)
    
    app = workflow.compile()
    result = app.invoke({"messages": [], "data": {}, "step_count": 0, "status": ""})
    
    print(f"\nPipeline completed: {result['status']}")
    print(f"Steps: {result['step_count']}")
    print()


def fan_out_fan_in_pattern():
    """Fan-out/fan-in pattern - parallel processing then merge"""
    print("=" * 60)
    print("Example 2: Fan-Out/Fan-In Pattern")
    print("=" * 60)
    
    def split_node(state: GraphState):
        """Split work into multiple tasks"""
        print("  [Split] Splitting work...")
        return {
            "data": {"tasks": ["task1", "task2", "task3"]},
            "step_count": state.get("step_count", 0) + 1
        }
    
    def process_task1(state: GraphState):
        """Process task 1"""
        print("  [Task1] Processing...")
        tasks = state["data"].get("tasks", [])
        results = state["data"].get("results", [])
        return {
            "data": {
                **state["data"],
                "results": results + [f"{tasks[0]}_completed"]
            },
            "step_count": state["step_count"] + 1
        }
    
    def process_task2(state: GraphState):
        """Process task 2"""
        print("  [Task2] Processing...")
        tasks = state["data"].get("tasks", [])
        results = state["data"].get("results", [])
        return {
            "data": {
                **state["data"],
                "results": results + [f"{tasks[1]}_completed"]
            },
            "step_count": state["step_count"] + 1
        }
    
    def merge_node(state: GraphState):
        """Merge results"""
        print("  [Merge] Merging results...")
        results = state["data"].get("results", [])
        return {
            "data": {**state["data"], "merged": True, "final_results": results},
            "step_count": state["step_count"] + 1,
            "status": "completed"
        }
    
    workflow = StateGraph(GraphState)
    workflow.add_node("split", split_node)
    workflow.add_node("task1", process_task1)
    workflow.add_node("task2", process_task2)
    workflow.add_node("merge", merge_node)
    
    workflow.set_entry_point("split")
    workflow.add_edge("split", "task1")
    workflow.add_edge("task1", "task2")  # Sequential for demo
    workflow.add_edge("task2", "merge")
    workflow.add_edge("merge", END)
    
    app = workflow.compile()
    result = app.invoke({"messages": [], "data": {}, "step_count": 0, "status": ""})
    
    print(f"\nFan-out/fan-in completed")
    print(f"Results: {result['data'].get('final_results', [])}")
    print()


def retry_pattern():
    """Retry pattern with conditional retry logic"""
    print("=" * 60)
    print("Example 3: Retry Pattern")
    print("=" * 60)
    
    def attempt_node(state: GraphState):
        """Attempt an operation"""
        attempt_count = state.get("data", {}).get("attempts", 0) + 1
        print(f"  [Attempt] Attempt #{attempt_count}")
        
        # Simulate success/failure
        success = attempt_count >= 3  # Succeed on 3rd attempt
        
        return {
            "data": {
                **state.get("data", {}),
                "attempts": attempt_count,
                "success": success
            },
            "step_count": state.get("step_count", 0) + 1
        }
    
    def check_success_node(state: GraphState):
        """Check if operation succeeded"""
        success = state["data"].get("success", False)
        return {
            "status": "success" if success else "retry_needed",
            "step_count": state["step_count"] + 1
        }
    
    def route_decision(state: GraphState) -> Literal["retry", "success"]:
        """Route based on success"""
        if state["status"] == "success":
            return "success"
        elif state["data"].get("attempts", 0) < 5:  # Max 5 attempts
            return "retry"
        else:
            return "success"  # Give up after max attempts
    
    workflow = StateGraph(GraphState)
    workflow.add_node("attempt", attempt_node)
    workflow.add_node("check", check_success_node)
    
    workflow.set_entry_point("attempt")
    workflow.add_edge("attempt", "check")
    workflow.add_conditional_edges(
        "check",
        route_decision,
        {
            "retry": "attempt",
            "success": END
        }
    )
    
    app = workflow.compile()
    result = app.invoke({"messages": [], "data": {}, "step_count": 0, "status": ""})
    
    print(f"\nRetry pattern completed")
    print(f"Attempts: {result['data'].get('attempts', 0)}")
    print(f"Status: {result['status']}")
    print()


def state_machine_pattern():
    """State machine pattern with explicit states"""
    print("=" * 60)
    print("Example 4: State Machine Pattern")
    print("=" * 60)
    
    def idle_node(state: GraphState):
        """Idle state"""
        print("  [State: IDLE]")
        return {
            "status": "processing",
            "step_count": state.get("step_count", 0) + 1
        }
    
    def processing_node(state: GraphState):
        """Processing state"""
        print("  [State: PROCESSING]")
        return {
            "status": "validating",
            "step_count": state["step_count"] + 1
        }
    
    def validating_node(state: GraphState):
        """Validating state"""
        print("  [State: VALIDATING]")
        return {
            "status": "completed",
            "step_count": state["step_count"] + 1
        }
    
    def route_by_status(state: GraphState) -> Literal["process", "validate", "complete"]:
        """Route based on status"""
        status = state.get("status", "idle")
        if status == "idle":
            return "process"
        elif status == "processing":
            return "validate"
        else:
            return "complete"
    
    workflow = StateGraph(GraphState)
    workflow.add_node("idle", idle_node)
    workflow.add_node("process", processing_node)
    workflow.add_node("validate", validating_node)
    
    workflow.set_entry_point("idle")
    workflow.add_conditional_edges(
        "idle",
        route_by_status,
        {
            "process": "process",
            "validate": "validate",
            "complete": END
        }
    )
    workflow.add_conditional_edges(
        "process",
        route_by_status,
        {
            "process": "process",
            "validate": "validate",
            "complete": END
        }
    )
    workflow.add_conditional_edges(
        "validate",
        route_by_status,
        {
            "process": "process",
            "validate": "validate",
            "complete": END
        }
    )
    
    app = workflow.compile()
    result = app.invoke({"messages": [], "data": {}, "step_count": 0, "status": "idle"})
    
    print(f"\nState machine completed")
    print(f"Final status: {result['status']}")
    print(f"Steps: {result['step_count']}")
    print()


def error_handling_pattern():
    """Error handling pattern with try-catch-like behavior"""
    print("=" * 60)
    print("Example 5: Error Handling Pattern")
    print("=" * 60)
    
    def risky_operation_node(state: GraphState):
        """Operation that might fail"""
        attempt = state.get("data", {}).get("operation_attempt", 0) + 1
        print(f"  [Risky Operation] Attempt {attempt}")
        
        # Simulate failure on first attempt
        if attempt == 1:
            return {
                "data": {
                    **state.get("data", {}),
                    "operation_attempt": attempt,
                    "error": "Operation failed"
                },
                "step_count": state.get("step_count", 0) + 1,
                "status": "error"
            }
        else:
            return {
                "data": {
                    **state.get("data", {}),
                    "operation_attempt": attempt,
                    "error": None
                },
                "step_count": state["step_count"] + 1,
                "status": "success"
            }
    
    def handle_error_node(state: GraphState):
        """Handle errors"""
        print("  [Error Handler] Handling error...")
        return {
            "data": {
                **state["data"],
                "error_handled": True
            },
            "status": "retry",
            "step_count": state["step_count"] + 1
        }
    
    def success_node(state: GraphState):
        """Handle success"""
        print("  [Success] Operation completed successfully")
        return {
            "status": "completed",
            "step_count": state["step_count"] + 1
        }
    
    def route_by_status(state: GraphState) -> Literal["retry", "success", "handle_error"]:
        """Route based on status"""
        status = state.get("status", "")
        if status == "error":
            return "handle_error"
        elif status == "success":
            return "success"
        else:
            return "retry"
    
    workflow = StateGraph(GraphState)
    workflow.add_node("risky_op", risky_operation_node)
    workflow.add_node("error_handler", handle_error_node)
    workflow.add_node("success", success_node)
    
    workflow.set_entry_point("risky_op")
    workflow.add_conditional_edges(
        "risky_op",
        route_by_status,
        {
            "retry": "risky_op",
            "success": "success",
            "handle_error": "error_handler"
        }
    )
    workflow.add_conditional_edges(
        "error_handler",
        route_by_status,
        {
            "retry": "risky_op",
            "success": "success",
            "handle_error": "error_handler"
        }
    )
    workflow.add_edge("success", END)
    
    app = workflow.compile()
    result = app.invoke({"messages": [], "data": {}, "step_count": 0, "status": ""})
    
    print(f"\nError handling pattern completed")
    print(f"Final status: {result['status']}")
    print(f"Attempts: {result['data'].get('operation_attempt', 0)}")
    print()


if __name__ == "__main__":
    try:
        pipeline_pattern()
        fan_out_fan_in_pattern()
        retry_pattern()
        state_machine_pattern()
        error_handling_pattern()
        
        print("=" * 60)
        print("All workflow pattern examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

