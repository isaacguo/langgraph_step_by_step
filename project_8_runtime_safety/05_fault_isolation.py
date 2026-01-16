"""
Runtime Safety - Fault Isolation
Demonstrates fault boundaries, error containment, and sandboxed execution
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Dict, Any, List, Literal, Optional
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()


class IsolationState(TypedDict):
    messages: Annotated[List[Dict], "messages"]
    agent_id: str
    fault_boundary: Optional[str]
    contained_errors: Annotated[List[str], "list of contained errors"]
    isolation_level: int
    sandbox_active: bool
    step_count: int


def fault_boundary_definition():
    """Define fault boundaries for isolation"""
    print("=" * 60)
    print("Example 1: Fault Boundary Definition")
    print("=" * 60)
    
    def define_boundary_node(state: IsolationState):
        """Define fault boundary"""
        print("  [Boundary] Defining fault boundary...")
        agent_id = state.get("agent_id", "agent_1")
        
        # Define boundary based on agent
        boundaries = {
            "agent_1": "data_processing",
            "agent_2": "api_interaction",
            "agent_3": "computation"
        }
        
        boundary = boundaries.get(agent_id, "default")
        
        return {
            "fault_boundary": boundary,
            "isolation_level": 1,
            "step_count": state.get("step_count", 0) + 1
        }
    
    def execute_with_boundary_node(state: IsolationState):
        """Execute within fault boundary"""
        print(f"  [Execution] Executing within boundary: {state.get('fault_boundary')}")
        return {
            "messages": state.get("messages", []) + [
                {"role": "system", "content": f"Executed within {state.get('fault_boundary')} boundary"}
            ],
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(IsolationState)
    workflow.add_node("define_boundary", define_boundary_node)
    workflow.add_node("execute", execute_with_boundary_node)
    
    workflow.set_entry_point("define_boundary")
    workflow.add_edge("define_boundary", "execute")
    workflow.add_edge("execute", END)
    
    app = workflow.compile()
    
    test_cases = [
        {
            "messages": [],
            "agent_id": "agent_1",
            "fault_boundary": None,
            "contained_errors": [],
            "isolation_level": 0,
            "sandbox_active": False,
            "step_count": 0
        },
        {
            "messages": [],
            "agent_id": "agent_2",
            "fault_boundary": None,
            "contained_errors": [],
            "isolation_level": 0,
            "sandbox_active": False,
            "step_count": 0
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}: Agent = {test_case['agent_id']}")
        result = app.invoke(test_case)
        print(f"  Fault boundary: {result['fault_boundary']}")
        print(f"  Isolation level: {result['isolation_level']}")
    print()


def error_containment_strategy():
    """Contain errors within boundaries"""
    print("=" * 60)
    print("Example 2: Error Containment Strategy")
    print("=" * 60)
    
    def risky_operation_node(state: IsolationState):
        """Operation that might fail"""
        print("  [Risky Operation] Executing risky operation...")
        step = state.get("step_count", 0) + 1
        
        # Simulate failure
        if step == 2:
            error = "Simulated error in risky operation"
            return {
                "contained_errors": state.get("contained_errors", []) + [error],
                "step_count": step
            }
        
        return {
            "step_count": step
        }
    
    def contain_error_node(state: IsolationState):
        """Contain error within boundary"""
        print("  [Containment] Containing error...")
        errors = state.get("contained_errors", [])
        boundary = state.get("fault_boundary", "unknown")
        
        if errors:
            return {
                "messages": state.get("messages", []) + [
                    {"role": "system", "content": f"Error contained within {boundary} boundary"}
                ],
                "isolation_level": 2,  # Increased isolation
                "step_count": state.get("step_count", 0) + 1
            }
        
        return {
            "isolation_level": 1,
            "step_count": state.get("step_count", 0) + 1
        }
    
    def route_by_error(state: IsolationState) -> Literal["contain", "continue"]:
        """Route based on error presence"""
        if state.get("contained_errors"):
            return "contain"
        return "continue"
    
    workflow = StateGraph(IsolationState)
    workflow.add_node("risky_op", risky_operation_node)
    workflow.add_node("contain", contain_error_node)
    
    workflow.set_entry_point("risky_op")
    workflow.add_conditional_edges(
        "risky_op",
        route_by_error,
        {
            "contain": "contain",
            "continue": END
        }
    )
    workflow.add_edge("contain", END)
    
    app = workflow.compile()
    
    test_case = {
        "messages": [],
        "agent_id": "agent_1",
        "fault_boundary": "data_processing",
        "contained_errors": [],
        "isolation_level": 1,
        "sandbox_active": False,
        "step_count": 0
    }
    
    # Execute twice to trigger error
    for i in range(2):
        test_case = app.invoke(test_case)
        print(f"\nExecution {i+1}:")
        print(f"  Step count: {test_case['step_count']}")
        print(f"  Contained errors: {len(test_case.get('contained_errors', []))}")
        print(f"  Isolation level: {test_case['isolation_level']}")
    print()


def sandboxed_execution():
    """Sandboxed execution environment"""
    print("=" * 60)
    print("Example 3: Sandboxed Execution")
    print("=" * 60)
    
    def activate_sandbox_node(state: IsolationState):
        """Activate sandbox"""
        print("  [Sandbox] Activating sandbox...")
        return {
            "sandbox_active": True,
            "isolation_level": 3,  # Highest isolation
            "step_count": state.get("step_count", 0) + 1
        }
    
    def sandboxed_operation_node(state: IsolationState):
        """Execute operation in sandbox"""
        print("  [Sandbox Operation] Executing in sandbox...")
        if not state.get("sandbox_active"):
            return {
                "contained_errors": state.get("contained_errors", []) + ["Operation attempted outside sandbox"],
                "step_count": state.get("step_count", 0) + 1
            }
        
        # Simulate operation that might fail
        try:
            # In real scenario, this would be actual risky code
            result = "sandbox_execution_successful"
            return {
                "messages": state.get("messages", []) + [
                    {"role": "system", "content": f"Sandbox execution: {result}"}
                ],
                "step_count": state.get("step_count", 0) + 1
            }
        except Exception as e:
            return {
                "contained_errors": state.get("contained_errors", []) + [str(e)],
                "step_count": state.get("step_count", 0) + 1
            }
    
    def deactivate_sandbox_node(state: IsolationState):
        """Deactivate sandbox"""
        print("  [Sandbox] Deactivating sandbox...")
        return {
            "sandbox_active": False,
            "isolation_level": 1,
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(IsolationState)
    workflow.add_node("activate", activate_sandbox_node)
    workflow.add_node("execute", sandboxed_operation_node)
    workflow.add_node("deactivate", deactivate_sandbox_node)
    
    workflow.set_entry_point("activate")
    workflow.add_edge("activate", "execute")
    workflow.add_edge("execute", "deactivate")
    workflow.add_edge("deactivate", END)
    
    app = workflow.compile()
    
    test_case = {
        "messages": [],
        "agent_id": "agent_1",
        "fault_boundary": "sandbox",
        "contained_errors": [],
        "isolation_level": 0,
        "sandbox_active": False,
        "step_count": 0
    }
    
    result = app.invoke(test_case)
    print(f"\nSandbox execution result:")
    print(f"  Sandbox active: {result['sandbox_active']}")
    print(f"  Isolation level: {result['isolation_level']}")
    print(f"  Contained errors: {len(result.get('contained_errors', []))}")
    print()


def multi_agent_fault_isolation():
    """Fault isolation in multi-agent systems"""
    print("=" * 60)
    print("Example 4: Multi-Agent Fault Isolation")
    print("=" * 60)
    
    def agent_a_node(state: IsolationState):
        """Agent A execution"""
        print("  [Agent A] Executing...")
        agent_id = state.get("agent_id", "")
        
        # Simulate agent-specific error
        if agent_id == "agent_a" and state.get("step_count", 0) == 1:
            return {
                "contained_errors": state.get("contained_errors", []) + ["Agent A error"],
                "fault_boundary": "agent_a_boundary",
                "step_count": state.get("step_count", 0) + 1
            }
        
        return {
            "step_count": state.get("step_count", 0) + 1
        }
    
    def agent_b_node(state: IsolationState):
        """Agent B execution - isolated from Agent A"""
        print("  [Agent B] Executing (isolated from Agent A)...")
        # Agent B should not be affected by Agent A's errors
        agent_a_errors = [e for e in state.get("contained_errors", []) if "Agent A" in e]
        
        if agent_a_errors:
            print("  [Agent B] Agent A errors detected but contained")
        
        return {
            "messages": state.get("messages", []) + [
                {"role": "agent_b", "content": "Agent B executed successfully despite Agent A errors"}
            ],
            "step_count": state.get("step_count", 0) + 1
        }
    
    def coordinator_node(state: IsolationState):
        """Coordinate agents with isolation"""
        print("  [Coordinator] Coordinating with fault isolation...")
        errors = state.get("contained_errors", [])
        
        return {
            "messages": state.get("messages", []) + [
                {"role": "coordinator", "content": f"Coordination complete. Contained errors: {len(errors)}"}
            ],
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(IsolationState)
    workflow.add_node("agent_a", agent_a_node)
    workflow.add_node("agent_b", agent_b_node)
    workflow.add_node("coordinator", coordinator_node)
    
    workflow.set_entry_point("agent_a")
    workflow.add_edge("agent_a", "agent_b")
    workflow.add_edge("agent_b", "coordinator")
    workflow.add_edge("coordinator", END)
    
    app = workflow.compile()
    
    test_case = {
        "messages": [],
        "agent_id": "agent_a",
        "fault_boundary": None,
        "contained_errors": [],
        "isolation_level": 1,
        "sandbox_active": False,
        "step_count": 0
    }
    
    result = app.invoke(test_case)
    print(f"\nMulti-agent isolation result:")
    print(f"  Contained errors: {len(result.get('contained_errors', []))}")
    print(f"  Fault boundary: {result.get('fault_boundary', 'none')}")
    print(f"  Messages: {len(result.get('messages', []))}")
    print()


def error_propagation_control():
    """Control error propagation across boundaries"""
    print("=" * 60)
    print("Example 5: Error Propagation Control")
    print("=" * 60)
    
    def propagate_decision_node(state: IsolationState):
        """Decide whether to propagate error"""
        print("  [Propagation Control] Evaluating error propagation...")
        errors = state.get("contained_errors", [])
        isolation_level = state.get("isolation_level", 1)
        
        # Higher isolation level = less propagation
        should_propagate = len(errors) > 0 and isolation_level < 2
        
        return {
            "data": {
                **state.get("data", {}),
                "error_propagation_allowed": should_propagate,
                "propagation_reason": "Low isolation level" if should_propagate else "High isolation level"
            },
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(IsolationState)
    workflow.add_node("propagate_decision", propagate_decision_node)
    workflow.set_entry_point("propagate_decision")
    workflow.add_edge("propagate_decision", END)
    
    app = workflow.compile()
    
    test_cases = [
        {
            "messages": [],
            "agent_id": "agent_1",
            "fault_boundary": "boundary_1",
            "contained_errors": ["Error 1"],
            "isolation_level": 1,  # Low isolation
            "sandbox_active": False,
            "step_count": 0,
            "data": {}
        },
        {
            "messages": [],
            "agent_id": "agent_2",
            "fault_boundary": "boundary_2",
            "contained_errors": ["Error 2"],
            "isolation_level": 3,  # High isolation
            "sandbox_active": False,
            "step_count": 0,
            "data": {}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}: Isolation level = {test_case['isolation_level']}")
        result = app.invoke(test_case)
        print(f"  Propagation allowed: {result.get('data', {}).get('error_propagation_allowed', False)}")
        print(f"  Reason: {result.get('data', {}).get('propagation_reason', 'N/A')}")
    print()


if __name__ == "__main__":
    try:
        fault_boundary_definition()
        error_containment_strategy()
        sandboxed_execution()
        multi_agent_fault_isolation()
        error_propagation_control()
        
        print("=" * 60)
        print("All fault isolation examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

