"""
LangGraph Basics - State Schemas
Demonstrates typed state management with Pydantic models
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


# Define Pydantic models for structured state
class Message(BaseModel):
    role: str = Field(description="Message role: user, assistant, or system")
    content: str = Field(description="Message content")
    timestamp: str = Field(default="", description="Message timestamp")


class UserProfile(BaseModel):
    name: str = Field(description="User name")
    preferences: List[str] = Field(default_factory=list, description="User preferences")
    session_id: str = Field(description="Session identifier")


# Define typed state
class GraphState(TypedDict):
    messages: Annotated[List[Message], "List of conversation messages"]
    user_profile: UserProfile
    current_step: str
    metadata: Annotated[dict, "Additional metadata"]


def typed_state_example():
    """Example with typed state using Pydantic models"""
    print("=" * 60)
    print("Example 1: Typed State with Pydantic Models")
    print("=" * 60)
    
    def initialize_node(state: GraphState):
        """Initialize state with typed models"""

        print("Executing: initialize_node")
        
        # Create typed objects
        messages = [
            Message(role="system", content="You are a helpful assistant", timestamp="2024-01-01T00:00:00")
        ]
        
        user_profile = UserProfile(
            name="Alice",
            preferences=["python", "machine learning"],
            session_id="session_123"
        )
        
        return {
            "messages": messages,
            "user_profile": user_profile,
            "current_step": "initialized",
            "metadata": {"version": "1.0"}
        }
    
    def process_node(state: GraphState):
        """Process with typed state"""
        print("Executing: process_node")
        
        # Access typed state
        current_messages = state["messages"]
        user_name = state["user_profile"].name
        
        # Add new typed message
        new_message = Message(
            role="user",
            content=f"Hello, my name is {user_name}",
            timestamp="2024-01-01T00:01:00"
        )
        
        return {
            "messages": current_messages + [new_message],
            "current_step": "processed"
        }
    
    def validate_node(state: GraphState):
        """Validate state structure"""
        print("Executing: validate_node")
        
        # Type checking happens automatically
        message_count = len(state["messages"])
        user_name = state["user_profile"].name
        
        validation_message = Message(
            role="system",
            content=f"Validated: {message_count} messages for user {user_name}",
            timestamp="2024-01-01T00:02:00"
        )
        
        return {
            "messages": state["messages"] + [validation_message],
            "current_step": "validated"
        }
    
    # Build graph
    workflow = StateGraph(GraphState)
    
    workflow.add_node("initialize", initialize_node)
    workflow.add_node("process", process_node)
    workflow.add_node("validate", validate_node)
    
    workflow.set_entry_point("initialize")
    workflow.add_edge("initialize", "process")
    workflow.add_edge("process", "validate")
    workflow.add_edge("validate", END)
    
    app = workflow.compile()
    
    # Execute with empty initial state (will be populated by initialize)
    initial_state: GraphState = {
        "messages": [],
        "user_profile": UserProfile(name="", session_id=""),
        "current_step": "",
        "metadata": {}
    }
    
    result = app.invoke(initial_state)
    
    print("\nFinal State:")
    print(f"Current step: {result['current_step']}")
    print(f"Message count: {len(result['messages'])}")
    print(f"User: {result['user_profile'].name}")
    print(f"Messages:")
    for msg in result["messages"]:
        print(f"  [{msg.role}]: {msg.content}")
    print()


def state_validation_example():
    """Example showing state validation"""
    print("=" * 60)
    print("Example 2: State Validation")
    print("=" * 60)
    
    def add_message_node(state: GraphState):
        """Add a message with validation"""
        print("Executing: add_message_node")
        
        # Create message with validation
        try:
            new_message = Message(
                role="assistant",
                content="This is a validated message",
                timestamp="2024-01-01T00:03:00"
            )
            
            return {
                "messages": state["messages"] + [new_message]
            }
        except Exception as e:
            print(f"Validation error: {e}")
            return state
    
    def check_state_integrity(state: GraphState):
        """Check state integrity"""
        print("Executing: check_state_integrity")
        
        # Access and validate all state components
        messages = state["messages"]
        profile = state["user_profile"]
        metadata = state["metadata"]
        
        print(f"State integrity check:")
        print(f"  Messages: {len(messages)} (all valid Message objects)")
        print(f"  Profile: {profile.name} (valid UserProfile)")
        print(f"  Metadata keys: {list(metadata.keys())}")
        
        return {
            "metadata": {**metadata, "integrity_check": "passed"}
        }
    
    # Build graph
    workflow = StateGraph(GraphState)
    
    workflow.add_node("add_message", add_message_node)
    workflow.add_node("check", check_state_integrity)
    
    workflow.set_entry_point("add_message")
    workflow.add_edge("add_message", "check")
    workflow.add_edge("check", END)
    
    app = workflow.compile()
    
    # Initialize with valid state
    initial_state: GraphState = {
        "messages": [
            Message(role="system", content="Initial message", timestamp="2024-01-01T00:00:00")
        ],
        "user_profile": UserProfile(name="Bob", session_id="session_456"),
        "current_step": "start",
        "metadata": {}
    }
    
    result = app.invoke(initial_state)
    
    print(f"\nFinal message count: {len(result['messages'])}")
    print(f"Integrity check: {result['metadata'].get('integrity_check', 'not performed')}")
    print()


def nested_state_example():
    """Example with nested state structures"""
    print("=" * 60)
    print("Example 3: Nested State Structures")
    print("=" * 60)
    
    class Task(BaseModel):
        id: str
        description: str
        status: str = Field(default="pending")
        assigned_to: str = ""
    
    class ProjectState(TypedDict):
        tasks: Annotated[List[Task], "List of tasks"]
        project_name: str
        team_members: Annotated[List[str], "Team member names"]
    
    def create_tasks_node(state: ProjectState):
        """Create initial tasks"""
        print("Executing: create_tasks_node")
        
        tasks = [
            Task(id="1", description="Design database schema", assigned_to="Alice"),
            Task(id="2", description="Implement API endpoints", assigned_to="Bob"),
            Task(id="3", description="Write unit tests", assigned_to="Charlie")
        ]
        
        return {
            "tasks": tasks,
            "project_name": "Web Application",
            "team_members": ["Alice", "Bob", "Charlie"]
        }
    
    def update_task_status_node(state: ProjectState):
        """Update task statuses"""
        print("Executing: update_task_status_node")
        
        updated_tasks = []
        for task in state["tasks"]:
            if task.id == "1":
                task.status = "completed"
            elif task.id == "2":
                task.status = "in_progress"
            updated_tasks.append(task)
        
        return {"tasks": updated_tasks}
    
    def generate_report_node(state: ProjectState):
        """Generate project report"""
        print("Executing: generate_report_node")
        
        completed = sum(1 for task in state["tasks"] if task.status == "completed")
        in_progress = sum(1 for task in state["tasks"] if task.status == "in_progress")
        pending = sum(1 for task in state["tasks"] if task.status == "pending")
        
        print(f"\nProject Report: {state['project_name']}")
        print(f"  Completed: {completed}")
        print(f"  In Progress: {in_progress}")
        print(f"  Pending: {pending}")
        print(f"  Team Members: {', '.join(state['team_members'])}")
        
        return state
    
    # Build graph
    workflow = StateGraph(ProjectState)
    
    workflow.add_node("create", create_tasks_node)
    workflow.add_node("update", update_task_status_node)
    workflow.add_node("report", generate_report_node)
    
    workflow.set_entry_point("create")
    workflow.add_edge("create", "update")
    workflow.add_edge("update", "report")
    workflow.add_edge("report", END)
    
    app = workflow.compile()
    
    initial_state: ProjectState = {
        "tasks": [],
        "project_name": "",
        "team_members": []
    }
    
    result = app.invoke(initial_state)
    
    print(f"\nFinal state:")
    print(f"  Project: {result['project_name']}")
    print(f"  Tasks: {len(result['tasks'])}")
    for task in result["tasks"]:
        print(f"    Task {task.id}: {task.description} - {task.status}")
    print()


if __name__ == "__main__":
    try:
        typed_state_example()
        state_validation_example()
        nested_state_example()
        
        print("=" * 60)
        print("All state schema examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

