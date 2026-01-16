"""
Memory Management - State Persistence
Demonstrates persisting state with checkpoints
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
load_dotenv()


class GraphState(TypedDict):
    messages: Annotated[list, "conversation messages"]
    data: dict
    step_count: int


def checkpoint_persistence_example():
    """Basic checkpoint persistence"""
    print("=" * 60)
    print("Example 1: Checkpoint Persistence")
    print("=" * 60)
    
    def process_node(state: GraphState):
        """Process and update state"""
        step = state.get("step_count", 0) + 1
        data = state.get("data", {})
        data[f"step_{step}"] = f"Processed at step {step}"
        
        return {
            "step_count": step,
            "data": data
        }
    
    # Build graph
    workflow = StateGraph(GraphState)
    workflow.add_node("process", process_node)
    workflow.set_entry_point("process")
    workflow.add_edge("process", END)
    
    # Use checkpoint
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    config = {"configurable": {"thread_id": "persist_thread_1"}}
    
    # Execute multiple times - state persists
    state = {"messages": [], "data": {}, "step_count": 0}
    
    print("Executing workflow multiple times...")
    for i in range(3):
        state = app.invoke(state, config)
        print(f"  Step {i+1}: {state['step_count']} steps, data keys: {list(state['data'].keys())}")
    
    print()


def state_recovery_example():
    """Recover state from checkpoint"""
    print("=" * 60)
    print("Example 2: State Recovery")
    print("=" * 60)
    
    def increment_node(state: GraphState):
        """Increment counter"""
        return {
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(GraphState)
    workflow.add_node("increment", increment_node)
    workflow.set_entry_point("increment")
    workflow.add_edge("increment", END)
    
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    thread_id = "recovery_thread_1"
    config = {"configurable": {"thread_id": thread_id}}
    
    # Initial execution
    state = {"messages": [], "data": {}, "step_count": 0}
    state = app.invoke(state, config)
    print(f"Initial execution: step_count = {state['step_count']}")
    
    # Simulate restart - recover state
    print("\nSimulating restart...")
    recovered_state = {"messages": [], "data": {}, "step_count": 0}
    recovered_state = app.invoke(recovered_state, config)
    print(f"After recovery: step_count = {recovered_state['step_count']}")
    print(f"State was persisted and recovered!")
    print()


def multiple_threads_example():
    """Multiple independent threads with separate state"""
    print("=" * 60)
    print("Example 3: Multiple Threads")
    print("=" * 60)
    
    def update_node(state: GraphState):
        """Update state"""
        step = state.get("step_count", 0) + 1
        thread_id = state.get("data", {}).get("thread_id", "unknown")
        
        return {
            "step_count": step,
            "data": {
                **state.get("data", {}),
                "thread_id": thread_id,
                f"update_{step}": f"Updated by {thread_id}"
            }
        }
    
    workflow = StateGraph(GraphState)
    workflow.add_node("update", update_node)
    workflow.set_entry_point("update")
    workflow.add_edge("update", END)
    
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    # Multiple threads
    threads = ["thread_a", "thread_b", "thread_c"]
    
    for thread_id in threads:
        config = {"configurable": {"thread_id": thread_id}}
        state = {
            "messages": [],
            "data": {"thread_id": thread_id},
            "step_count": 0
        }
        
        # Execute twice for each thread
        for i in range(2):
            state = app.invoke(state, config)
        
        print(f"Thread {thread_id}: step_count = {state['step_count']}, "
              f"data keys = {list(state['data'].keys())}")
    
    print()


if __name__ == "__main__":
    try:
        checkpoint_persistence_example()
        state_recovery_example()
        multiple_threads_example()
        
        print("=" * 60)
        print("All state persistence examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

