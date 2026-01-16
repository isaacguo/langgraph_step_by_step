"""
Agent Communication - Supervisor Pattern
Demonstrates supervisor-agent architecture with task delegation
"""

import os
import sys
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


class SupervisorState(TypedDict):
    messages: Annotated[list, "conversation messages"]
    task: str
    assigned_agent: str
    result: str
    step_count: int


def create_supervisor_agent():
    """Create a supervisor agent that delegates tasks"""
    llm = get_local_llm(temperature=0.3)
    
    def supervisor_node(state: SupervisorState):
        """Supervisor agent that assigns tasks"""
        print("  [Supervisor] Analyzing task and assigning to appropriate agent...")
        task = state.get("task", "")
        
        prompt = ChatPromptTemplate.from_template(
            "You are a supervisor agent. Analyze this task and determine which specialist agent should handle it. "
            "Respond with only one word: 'researcher', 'writer', 'coder', or 'analyst'.\n\n"
            "Task: {task}"
        )
        chain = prompt | llm
        response = chain.invoke({"task": task})
        
        assigned_agent = response.content.strip().lower()
        # Normalize response
        if "research" in assigned_agent:
            assigned_agent = "researcher"
        elif "write" in assigned_agent or "writer" in assigned_agent:
            assigned_agent = "writer"
        elif "code" in assigned_agent or "coder" in assigned_agent:
            assigned_agent = "coder"
        else:
            assigned_agent = "analyst"
        
        return {
            "messages": state.get("messages", []) + [
                {"role": "supervisor", "content": f"Assigned to {assigned_agent} agent"}
            ],
            "assigned_agent": assigned_agent,
            "step_count": state.get("step_count", 0) + 1
        }
    
    return supervisor_node


def create_researcher_agent():
    """Create researcher specialist agent"""
    llm = get_local_llm(temperature=0.7)
    
    def researcher_node(state: SupervisorState):
        """Researcher agent"""
        print("  [Researcher Agent] Conducting research...")
        task = state.get("task", "")
        
        prompt = ChatPromptTemplate.from_template(
            "As a research specialist, provide comprehensive research on: {task}"
        )
        chain = prompt | llm
        response = chain.invoke({"task": task})
        
        return {
            "messages": state.get("messages", []) + [
                {"role": "researcher", "content": response.content}
            ],
            "result": response.content,
            "step_count": state["step_count"] + 1
        }
    
    return researcher_node


def create_writer_agent():
    """Create writer specialist agent"""
    llm = get_local_llm(temperature=0.8)
    
    def writer_node(state: SupervisorState):
        """Writer agent"""
        print("  [Writer Agent] Creating content...")
        task = state.get("task", "")
        
        prompt = ChatPromptTemplate.from_template(
            "As a writing specialist, create engaging content about: {task}"
        )
        chain = prompt | llm
        response = chain.invoke({"task": task})
        
        return {
            "messages": state.get("messages", []) + [
                {"role": "writer", "content": response.content}
            ],
            "result": response.content,
            "step_count": state["step_count"] + 1
        }
    
    return writer_node


def create_coder_agent():
    """Create coder specialist agent"""
    llm = get_local_llm(temperature=0.5)
    
    def coder_node(state: SupervisorState):
        """Coder agent"""
        print("  [Coder Agent] Writing code...")
        task = state.get("task", "")
        
        prompt = ChatPromptTemplate.from_template(
            "As a coding specialist, write code or provide a coding solution for: {task}"
        )
        chain = prompt | llm
        response = chain.invoke({"task": task})
        
        return {
            "messages": state.get("messages", []) + [
                {"role": "coder", "content": response.content}
            ],
            "result": response.content,
            "step_count": state["step_count"] + 1
        }
    
    return coder_node


def create_analyst_agent():
    """Create analyst specialist agent"""
    llm = get_local_llm(temperature=0.4)
    
    def analyst_node(state: SupervisorState):
        """Analyst agent"""
        print("  [Analyst Agent] Performing analysis...")
        task = state.get("task", "")
        
        prompt = ChatPromptTemplate.from_template(
            "As an analyst specialist, provide detailed analysis of: {task}"
        )
        chain = prompt | llm
        response = chain.invoke({"task": task})
        
        return {
            "messages": state.get("messages", []) + [
                {"role": "analyst", "content": response.content}
            ],
            "result": response.content,
            "step_count": state["step_count"] + 1
        }
    
    return analyst_node


def supervisor_pattern_example():
    """Supervisor pattern with task delegation"""
    print("=" * 60)
    print("Example 1: Supervisor Pattern with Task Delegation")
    print("=" * 60)
    
    # Create agents
    supervisor = create_supervisor_agent()
    researcher = create_researcher_agent()
    writer = create_writer_agent()
    coder = create_coder_agent()
    analyst = create_analyst_agent()
    
    def route_to_agent(state: SupervisorState) -> Literal["researcher", "writer", "coder", "analyst"]:
        """Route to assigned agent"""
        return state.get("assigned_agent", "analyst")
    
    # Build graph
    workflow = StateGraph(SupervisorState)
    
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("researcher", researcher)
    workflow.add_node("writer", writer)
    workflow.add_node("coder", coder)
    workflow.add_node("analyst", analyst)
    
    workflow.set_entry_point("supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "researcher": "researcher",
            "writer": "writer",
            "coder": "coder",
            "analyst": "analyst"
        }
    )
    workflow.add_edge("researcher", END)
    workflow.add_edge("writer", END)
    workflow.add_edge("coder", END)
    workflow.add_edge("analyst", END)
    
    app = workflow.compile()
    
    # Test with different tasks
    test_tasks = [
        "Research the latest AI developments",
        "Write a blog post about Python",
        "Create a function to sort a list",
        "Analyze market trends in tech"
    ]
    
    for task in test_tasks:
        print(f"\nTask: {task}")
        initial_state = {
            "messages": [],
            "task": task,
            "assigned_agent": "",
            "result": "",
            "step_count": 0
        }
        
        result = app.invoke(initial_state)
        print(f"Assigned to: {result['assigned_agent']}")
        print(f"Result preview: {result['result'][:100]}...")
    print()


def supervisor_with_feedback():
    """Supervisor pattern with feedback loop"""
    print("=" * 60)
    print("Example 2: Supervisor with Feedback Loop")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.3)
    
    def supervisor_node(state: SupervisorState):
        """Supervisor with review capability"""
        print("  [Supervisor] Reviewing work...")
        result = state.get("result", "")
        
        if not result:
            # Initial assignment
            task = state.get("task", "")
            prompt = ChatPromptTemplate.from_template(
                "Assign this task to an agent (respond with: researcher, writer, coder, or analyst): {task}"
            )
            chain = prompt | llm
            response = chain.invoke({"task": task})
            assigned = response.content.strip().lower()
            
            if "research" in assigned:
                assigned = "researcher"
            elif "write" in assigned:
                assigned = "writer"
            elif "code" in assigned:
                assigned = "coder"
            else:
                assigned = "analyst"
            
            return {
                "assigned_agent": assigned,
                "step_count": state.get("step_count", 0) + 1
            }
        else:
            # Review result
            prompt = ChatPromptTemplate.from_template(
                "Review this work. If it needs improvement, respond with 'improve', otherwise 'complete': {result}"
            )
            chain = prompt | llm
            response = chain.invoke({"result": result[:500]})  # Limit length
            
            needs_improvement = "improve" in response.content.lower()
            
            return {
                "messages": state.get("messages", []) + [
                    {"role": "supervisor", "content": response.content}
                ],
                "needs_improvement": needs_improvement,
                "step_count": state["step_count"] + 1
            }
    
    def worker_agent(state: SupervisorState):
        """Generic worker agent"""
        print(f"  [Worker Agent: {state.get('assigned_agent', 'unknown')}] Working...")
        task = state.get("task", "")
        agent_type = state.get("assigned_agent", "analyst")
        
        prompts = {
            "researcher": "Research: {task}",
            "writer": "Write about: {task}",
            "coder": "Code solution for: {task}",
            "analyst": "Analyze: {task}"
        }
        
        prompt_text = prompts.get(agent_type, prompts["analyst"])
        prompt = ChatPromptTemplate.from_template(prompt_text)
        llm = get_local_llm(temperature=0.7)
        chain = prompt | llm
        response = chain.invoke({"task": task})
        
        return {
            "messages": state.get("messages", []) + [
                {"role": agent_type, "content": response.content}
            ],
            "result": response.content,
            "step_count": state["step_count"] + 1
        }
    
    def route_decision(state: SupervisorState) -> Literal["worker", "complete"]:
        """Route decision"""
        if state.get("assigned_agent") and not state.get("result"):
            return "worker"
        elif state.get("needs_improvement", False):
            return "worker"
        else:
            return "complete"
    
    # Build graph
    workflow = StateGraph(SupervisorState)
    
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("worker", worker_agent)
    
    workflow.set_entry_point("supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        route_decision,
        {
            "worker": "worker",
            "complete": END
        }
    )
    workflow.add_edge("worker", "supervisor")  # Feedback loop
    
    app = workflow.compile()
    
    initial_state = {
        "messages": [],
        "task": "Explain machine learning",
        "assigned_agent": "",
        "result": "",
        "step_count": 0
    }
    
    result = app.invoke(initial_state)
    
    print("\nSupervisor feedback loop completed!")
    print(f"Total steps: {result['step_count']}")
    print(f"Final agent: {result.get('assigned_agent', 'unknown')}")
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
        supervisor_pattern_example()
        supervisor_with_feedback()
        
        print("=" * 60)
        print("All supervisor pattern examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

