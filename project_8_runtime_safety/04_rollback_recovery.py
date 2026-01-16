"""
Runtime Safety - Rollback & Recovery
Demonstrates deterministic rollback, checkpointing, and state restoration
"""

import os
import json
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from datetime import datetime

# Load environment variables
load_dotenv()


class RollbackState(TypedDict):
    messages: Annotated[List[Dict], "conversation messages"]
    data: Dict[str, Any]
    current_checkpoint: Optional[str]  # Renamed from checkpoint_id (reserved by LangGraph)
    checkpoint_history: Annotated[List[str], "list of checkpoint IDs"]
    rollback_requested: bool
    recovery_path: Annotated[List[str], "recovery steps taken"]
    step_count: int


def checkpoint_creation():
    """Create checkpoints at critical points"""
    print("=" * 60)
    print("Example 1: Checkpoint Creation")
    print("=" * 60)
    
    def create_checkpoint_node(state: RollbackState):
        """Create a checkpoint"""
        print("  [Checkpoint] Creating checkpoint...")
        checkpoint_id = f"checkpoint_{state.get('step_count', 0)}_{datetime.now().isoformat()}"
        checkpoint_history = state.get("checkpoint_history", [])
        
        # Store checkpoint data
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "timestamp": datetime.now().isoformat(),
            "state_snapshot": {
                "messages": state.get("messages", []),
                "data": state.get("data", {}),
                "step_count": state.get("step_count", 0)
            }
        }
        
        return {
            "current_checkpoint": checkpoint_id,
            "checkpoint_history": checkpoint_history + [checkpoint_id],
            "data": {
                **state.get("data", {}),
                f"checkpoint_{checkpoint_id}": checkpoint_data
            },
            "step_count": state.get("step_count", 0) + 1
        }
    
    def process_node(state: RollbackState):
        """Process and update state"""
        print("  [Process] Processing...")
        return {
            "data": {
                **state.get("data", {}),
                "processed": True,
                "value": state.get("step_count", 0) * 10
            },
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(RollbackState)
    workflow.add_node("checkpoint", create_checkpoint_node)
    workflow.add_node("process", process_node)
    
    workflow.set_entry_point("checkpoint")
    workflow.add_edge("checkpoint", "process")
    workflow.add_edge("process", END)
    
    app = workflow.compile()
    
    initial_state = {
        "messages": [],
        "data": {"initial": True},
        "current_checkpoint": None,
        "checkpoint_history": [],
        "rollback_requested": False,
        "recovery_path": [],
        "step_count": 0
    }
    
    result = app.invoke(initial_state)
    print(f"\nCheckpoint created: {result['current_checkpoint']}")
    print(f"Checkpoint history: {len(result['checkpoint_history'])} checkpoints")
    print()


def deterministic_rollback():
    """Perform deterministic rollback to a checkpoint"""
    print("=" * 60)
    print("Example 2: Deterministic Rollback")
    print("=" * 60)
    
    def rollback_node(state: RollbackState):
        """Rollback to a checkpoint"""
        print("  [Rollback] Rolling back to checkpoint...")
        checkpoint_history = state.get("checkpoint_history", [])
        target_checkpoint = state.get("current_checkpoint")
        
        if not target_checkpoint or target_checkpoint not in checkpoint_history:
            return {
                "recovery_path": state.get("recovery_path", []) + ["rollback_failed"],
                "step_count": state.get("step_count", 0) + 1
            }
        
        # Find checkpoint data
        checkpoint_data_key = f"checkpoint_{target_checkpoint}"
        checkpoint_data = state.get("data", {}).get(checkpoint_data_key, {})
        
        if not checkpoint_data:
            return {
                "recovery_path": state.get("recovery_path", []) + ["checkpoint_not_found"],
                "step_count": state.get("step_count", 0) + 1
            }
        
        # Restore state from checkpoint
        snapshot = checkpoint_data.get("state_snapshot", {})
        
        return {
            "messages": snapshot.get("messages", []),
            "data": {
                **snapshot.get("data", {}),
                "rolled_back": True,
                "rollback_to": target_checkpoint
            },
            "step_count": snapshot.get("step_count", 0),
            "recovery_path": state.get("recovery_path", []) + [f"rolled_back_to_{target_checkpoint}"]
        }
    
    workflow = StateGraph(RollbackState)
    workflow.add_node("rollback", rollback_node)
    workflow.set_entry_point("rollback")
    workflow.add_edge("rollback", END)
    
    app = workflow.compile()
    
    # Create a state with checkpoint history
    checkpoint_id = "checkpoint_0_2024-01-01T00:00:00"
    state = {
        "messages": [{"role": "user", "content": "test"}],
        "data": {
            "initial": True,
            f"checkpoint_{checkpoint_id}": {
                "checkpoint_id": checkpoint_id,
                "timestamp": "2024-01-01T00:00:00",
                "state_snapshot": {
                    "messages": [],
                    "data": {"initial": True},
                    "step_count": 0
                }
            }
        },
        "current_checkpoint": checkpoint_id,
        "checkpoint_history": [checkpoint_id],
        "rollback_requested": True,
        "recovery_path": [],
        "step_count": 5  # Current step is 5, will rollback to 0
    }
    
    result = app.invoke(state)
    print(f"\nRollback result:")
    print(f"  Rolled back to step: {result['step_count']}")
    print(f"  Recovery path: {result['recovery_path']}")
    print(f"  Data after rollback: {result['data'].get('rolled_back', False)}")
    print()


def state_restoration():
    """Restore state from checkpoint"""
    print("=" * 60)
    print("Example 3: State Restoration")
    print("=" * 60)
    
    def restore_state_node(state: RollbackState):
        """Restore state from checkpoint"""
        print("  [Restore] Restoring state...")
        checkpoint_id = state.get("current_checkpoint")
        
        if not checkpoint_id:
            return {
                "recovery_path": state.get("recovery_path", []) + ["no_checkpoint_specified"],
                "step_count": state.get("step_count", 0) + 1
            }
        
        # In a real system, this would load from persistent storage
        # For demo, we simulate restoration
        checkpoint_data_key = f"checkpoint_{checkpoint_id}"
        checkpoint_data = state.get("data", {}).get(checkpoint_data_key)
        
        if checkpoint_data:
            snapshot = checkpoint_data.get("state_snapshot", {})
            restored_state = {
                "messages": snapshot.get("messages", []),
                "data": {
                    **snapshot.get("data", {}),
                    "restored": True,
                    "restore_timestamp": datetime.now().isoformat()
                },
                "step_count": snapshot.get("step_count", 0),
                "recovery_path": state.get("recovery_path", []) + ["state_restored"]
            }
            return restored_state
        
        return {
            "recovery_path": state.get("recovery_path", []) + ["restore_failed"],
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(RollbackState)
    workflow.add_node("restore", restore_state_node)
    workflow.set_entry_point("restore")
    workflow.add_edge("restore", END)
    
    app = workflow.compile()
    
    checkpoint_id = "checkpoint_restore_1"
    state = {
        "messages": [],
        "data": {
            f"checkpoint_{checkpoint_id}": {
                "checkpoint_id": checkpoint_id,
                "timestamp": datetime.now().isoformat(),
                "state_snapshot": {
                    "messages": [{"role": "system", "content": "Restored message"}],
                    "data": {"original": True, "value": 42},
                    "step_count": 2
                }
            }
        },
        "current_checkpoint": checkpoint_id,
        "checkpoint_history": [checkpoint_id],
        "rollback_requested": False,
        "recovery_path": [],
        "step_count": 10  # Current state is at step 10
    }
    
    result = app.invoke(state)
    print(f"\nState restoration result:")
    print(f"  Restored to step: {result['step_count']}")
    print(f"  Messages restored: {len(result['messages'])}")
    print(f"  Data restored: {result['data'].get('restored', False)}")
    print(f"  Original value: {result['data'].get('value', 'N/A')}")
    print()


def recovery_path_execution():
    """Execute recovery path after rollback"""
    print("=" * 60)
    print("Example 4: Recovery Path Execution")
    print("=" * 60)
    
    def detect_failure_node(state: RollbackState):
        """Detect failure and trigger recovery"""
        print("  [Failure Detection] Detecting failure...")
        # Simulate failure detection
        has_failure = state.get("data", {}).get("failure_detected", False)
        
        if has_failure:
            return {
                "rollback_requested": True,
                "recovery_path": state.get("recovery_path", []) + ["failure_detected"],
                "step_count": state.get("step_count", 0) + 1
            }
        
        return {
            "rollback_requested": False,
            "step_count": state.get("step_count", 0) + 1
        }
    
    def execute_recovery_node(state: RollbackState):
        """Execute recovery steps"""
        print("  [Recovery] Executing recovery path...")
        recovery_path = state.get("recovery_path", [])
        
        # Recovery steps
        recovery_steps = [
            "validate_checkpoint",
            "restore_state",
            "verify_integrity",
            "resume_operation"
        ]
        
        updated_path = recovery_path + recovery_steps
        
        return {
            "recovery_path": updated_path,
            "data": {
                **state.get("data", {}),
                "recovery_completed": True,
                "recovery_steps": len(recovery_steps)
            },
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(RollbackState)
    workflow.add_node("detect_failure", detect_failure_node)
    workflow.add_node("execute_recovery", execute_recovery_node)
    
    workflow.set_entry_point("detect_failure")
    workflow.add_edge("detect_failure", "execute_recovery")
    workflow.add_edge("execute_recovery", END)
    
    app = workflow.compile()
    
    test_cases = [
        {
            "messages": [],
            "data": {"failure_detected": True},
            "current_checkpoint": None,
            "checkpoint_history": [],
            "rollback_requested": False,
            "recovery_path": [],
            "step_count": 0
        },
        {
            "messages": [],
            "data": {"failure_detected": False},
            "current_checkpoint": None,
            "checkpoint_history": [],
            "rollback_requested": False,
            "recovery_path": [],
            "step_count": 0
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}: Failure detected = {test_case['data'].get('failure_detected', False)}")
        result = app.invoke(test_case)
        print(f"  Rollback requested: {result['rollback_requested']}")
        print(f"  Recovery path steps: {len(result['recovery_path'])}")
        if result.get("data", {}).get("recovery_completed"):
            print(f"  Recovery completed: {result['data']['recovery_completed']}")
    print()


def checkpoint_with_memory():
    """Use LangGraph's checkpoint memory for rollback"""
    print("=" * 60)
    print("Example 5: Checkpoint with LangGraph Memory")
    print("=" * 60)
    
    def increment_node(state: RollbackState):
        """Increment counter"""
        return {
            "step_count": state.get("step_count", 0) + 1,
            "data": {
                **state.get("data", {}),
                "counter": state.get("data", {}).get("counter", 0) + 1
            }
        }
    
    workflow = StateGraph(RollbackState)
    workflow.add_node("increment", increment_node)
    workflow.set_entry_point("increment")
    workflow.add_edge("increment", END)
    
    # Use memory checkpoint
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    config = {"configurable": {"thread_id": "rollback_thread_1"}}
    
    # Execute multiple steps
    state = {
        "messages": [],
        "data": {"counter": 0},
        "current_checkpoint": None,
        "checkpoint_history": [],
        "rollback_requested": False,
        "recovery_path": [],
        "step_count": 0
    }
    
    print("Executing workflow with checkpoints...")
    for i in range(3):
        state = app.invoke(state, config)
        print(f"  Step {i+1}: counter = {state['data'].get('counter', 0)}, step_count = {state['step_count']}")
    
    # Simulate rollback by restoring from checkpoint
    print("\nSimulating rollback...")
    # In real scenario, you would use app.get_state() to retrieve checkpoint
    print("  Checkpoint system maintains state history for rollback")
    print()


if __name__ == "__main__":
    try:
        checkpoint_creation()
        deterministic_rollback()
        state_restoration()
        recovery_path_execution()
        checkpoint_with_memory()
        
        print("=" * 60)
        print("All rollback and recovery examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

