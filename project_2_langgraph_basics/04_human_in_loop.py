"""
LangGraph Basics - Human-in-the-Loop
Demonstrates human interaction patterns in graphs
"""

import os
import sys
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Add utils to path for utility function
_file_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_file_dir, '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from utils.llm_config import get_local_llm

# Load environment variables
load_dotenv()


class GraphState(TypedDict):
    messages: Annotated[list, "list of messages"]
    user_input: str
    approval_status: str
    step_count: int
    needs_clarification: bool  # Flag to indicate if human clarification is needed


def human_approval_example():
    """Example requiring human approval before proceeding"""
    print("=" * 60)
    print("Example 1: Human Approval Checkpoint")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.7)
    
    def generate_proposal_node(state: GraphState):
        """Generate a proposal"""
        print("Executing: generate_proposal_node")
        user_input = state.get("user_input", "Create a marketing campaign")
        
        proposal = f"Proposal for: {user_input}\n\nThis proposal requires approval before execution."
        
        return {
            "messages": state.get("messages", []) + [
                {"role": "assistant", "content": proposal}
            ],
            "step_count": state.get("step_count", 0) + 1
        }
    
    def execute_node(state: GraphState):
        """Execute after approval"""
        print("Executing: execute_node")
        approval = state.get("approval_status", "pending")
        
        if approval == "approved":
            return {
                "messages": state["messages"] + [
                    {"role": "system", "content": "Execution completed with approval."}
                ],
                "step_count": state["step_count"] + 1
            }
        else:
            return {
                "messages": state["messages"] + [
                    {"role": "system", "content": "Execution cancelled - approval not granted."}
                ],
                "step_count": state["step_count"] + 1
            }
    
    # Build graph with interrupt
    workflow = StateGraph(GraphState)
    
    workflow.add_node("generate", generate_proposal_node)
    workflow.add_node("execute", execute_node)
    
    workflow.set_entry_point("generate")
    
    # Add interrupt before execution (requires human approval)
    workflow.add_edge("generate", "execute")
    workflow.add_edge("execute", END)
    
    # Compile with memory for state persistence and interrupt before execute
    memory = MemorySaver()
    # Use interrupt_before to pause before execute node, waiting for human approval
    app = workflow.compile(checkpointer=memory, interrupt_before=["execute"])
    
    # Simulate workflow execution
    config = {"configurable": {"thread_id": "approval_thread_1"}}
    
    initial_state = {
        "messages": [],
        "user_input": "Launch new product",
        "approval_status": "pending",
        "step_count": 0
    }
    
    # First invocation - generates proposal and stops at interrupt (before execute)
    print("\nStep 1: Generating proposal...")
    result1 = app.invoke(initial_state, config)
    print(f"Proposal generated. Step count: {result1['step_count']}")
    print(f"Last message: {result1['messages'][-1].get('content', '')[:100]}")
    print("Workflow paused at interrupt - waiting for approval...")
    
    # Simulate human approval (in real scenario, this would be interactive)
    print("\nStep 2: Simulating human approval...")
    # Update approval status and continue from checkpoint
    # Get the current state and update approval_status
    approved_state = {
        **result1,
        "approval_status": "approved"  # Human approves
    }
    
    # Continue from checkpoint - this will resume from the interrupt
    result2 = app.invoke(approved_state, config)
    print(f"Execution completed. Step count: {result2['step_count']}")
    print(f"Final message: {result2['messages'][-1].get('content', '')[:100]}")
    print()


def interactive_workflow_example():
    """Example of interactive workflow with multiple checkpoints"""
    print("=" * 60)
    print("Example 2: Interactive Workflow")
    print("=" * 60)
    
    def step1_node(state: GraphState):
        """First step"""
        print("Executing: step1_node")
        return {
            "messages": state.get("messages", []) + [{"content": "Step 1 completed"}],
            "step_count": state.get("step_count", 0) + 1
        }
    
    def step2_node(state: GraphState):
        """Second step - requires input"""
        print("Executing: step2_node")
        user_input = state.get("user_input", "")
        return {
            "messages": state["messages"] + [
                {"content": f"Step 2 processed: {user_input}"}
            ],
            "step_count": state["step_count"] + 1
        }
    
    def step3_node(state: GraphState):
        """Third step"""
        print("Executing: step3_node")
        return {
            "messages": state["messages"] + [{"content": "Step 3 completed"}],
            "step_count": state["step_count"] + 1
        }
    
    # Build graph with interrupts between steps
    workflow = StateGraph(GraphState)
    
    workflow.add_node("step1", step1_node)
    workflow.add_node("step2", step2_node)
    workflow.add_node("step3", step3_node)
    
    workflow.set_entry_point("step1")
    workflow.add_edge("step1", "step2")
    workflow.add_edge("step2", "step3")
    workflow.add_edge("step3", END)
    
    memory = MemorySaver()
    # Add interrupts after each step to allow step-by-step execution
    app = workflow.compile(checkpointer=memory, interrupt_after=["step1", "step2"])
    
    config = {"configurable": {"thread_id": "interactive_thread_1"}}
    
    # Execute step by step
    state = {
        "messages": [],
        "user_input": "",
        "approval_status": "",
        "step_count": 0
    }
    
    print("\nExecuting workflow step by step...")
    
    # Step 1 - will stop at interrupt_after
    state = app.invoke(state, config)
    print(f"After step 1: {state['step_count']} steps completed")
    print(f"Messages so far: {len(state['messages'])}")
    
    # Update state with user input (simulating human interaction)
    state["user_input"] = "User provided input here"
    
    # Step 2 - will stop at interrupt_after
    state = app.invoke(state, config)
    print(f"After step 2: {state['step_count']} steps completed")
    print(f"Messages so far: {len(state['messages'])}")
    
    # Step 3 - will complete the workflow
    state = app.invoke(state, config)
    print(f"After step 3: {state['step_count']} steps completed")
    
    print(f"\nFinal state: {len(state['messages'])} messages")
    print()


def conditional_human_input():
    """Example where human input is conditionally required"""
    print("=" * 60)
    print("Example 3: Conditional Human Input")
    print("=" * 60)
    
    def analyze_node(state: GraphState):
        """Analyze if human input is needed"""
        print("Executing: analyze_node")
        user_input = state.get("user_input", "").lower()
        
        # Determine if clarification is needed
        needs_clarification = len(user_input) < 10 or "?" in user_input
        print(f"  → user_input: '{user_input}'")
        print(f"  → needs_clarification calculated: {needs_clarification}")
        
        # Return complete state update including all required fields
        result = {
            "messages": state.get("messages", []) + [
                {"content": f"Analysis: {'Needs clarification' if needs_clarification else 'Clear request'}"}
            ],
            "needs_clarification": needs_clarification,
            "step_count": state.get("step_count", 0) + 1,
            "user_input": state.get("user_input", ""),  # Preserve user_input
            "approval_status": state.get("approval_status", "")  # Preserve approval_status
        }
        print(f"  → Returning needs_clarification: {result['needs_clarification']}")
        print(f"  → Returning state keys: {list(result.keys())}")
        return result
    
    def clarify_node(state: GraphState):
        """Request clarification from human"""
        print("Executing: clarify_node")
        return {
            "messages": state["messages"] + [
                {"content": "Please provide more details to proceed."}
            ],
            "step_count": state["step_count"] + 1
        }
    
    def process_node(state: GraphState):
        """Process the request"""
        print("Executing: process_node")
        return {
            "messages": state["messages"] + [
                {"content": "Processing your request..."}
            ],
            "step_count": state["step_count"] + 1
        }
    
    def route_decision(state: GraphState) -> str:
        """Route based on whether clarification is needed"""
        # Access needs_clarification directly from state (set by analyze_node)
        # In LangGraph, conditional edge functions receive the merged state after node execution
        needs_clarification = state.get("needs_clarification", False)
        print(f"  → Route decision: needs_clarification = {needs_clarification}")
        print(f"  → State contains needs_clarification: {'needs_clarification' in state}")
        if "needs_clarification" in state:
            print(f"  → needs_clarification value: {state['needs_clarification']}")
        if needs_clarification:
            print("  → Routing to: clarify")
            return "clarify"
        else:
            print("  → Routing to: process")
            return "process"
    
    # Build graph
    workflow = StateGraph(GraphState)
    
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("clarify", clarify_node)
    workflow.add_node("process", process_node)
    
    workflow.set_entry_point("analyze")
    workflow.add_conditional_edges(
        "analyze",
        route_decision,
        {
            "clarify": "clarify",
            "process": "process"
        }
    )
    workflow.add_edge("clarify", END)  # Stops for human input
    workflow.add_edge("process", END)
    
    # Try without checkpointer first to see if that's the issue
    # memory = MemorySaver()
    # app = workflow.compile(checkpointer=memory)
    app = workflow.compile()  # Compile without checkpointer to test
    
    # config = {"configurable": {"thread_id": "conditional_thread_1"}}  # Not needed without checkpointer
    config = {}  # Empty config when not using checkpointer
    
    # Test case 1: Needs clarification
    print("\nTest 1: Short input (needs clarification)")
    state1 = {
        "messages": [],
        "user_input": "help?",
        "approval_status": "",
        "step_count": 0
        # needs_clarification will be set by analyze_node
    }
    result1 = app.invoke(state1, config)
    print(f"Result: {result1['messages'][-1].get('content', '')}")
    print(f"Route taken: {'clarify' if result1.get('needs_clarification', False) else 'process'}")
    
    # Test case 2: Clear input
    print("\nTest 2: Clear input (no clarification needed)")
    state2 = {
        "messages": [],
        "user_input": "Create a comprehensive report on machine learning trends",
        "approval_status": "",
        "step_count": 0
        # needs_clarification will be set by analyze_node
    }
    result2 = app.invoke(state2, config)
    print(f"Result: {result2['messages'][-1].get('content', '')}")
    print(f"Route taken: {'clarify' if result2.get('needs_clarification', False) else 'process'}")
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
        human_approval_example()
        interactive_workflow_example()
        conditional_human_input()
        
        print("=" * 60)
        print("All human-in-the-loop examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

