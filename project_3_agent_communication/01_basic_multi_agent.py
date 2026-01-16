"""
Agent Communication - Basic Multi-Agent System
Demonstrates a simple multi-agent setup with different agent roles
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


class AgentState(TypedDict):
    messages: Annotated[list, "conversation messages"]
    current_agent: str
    task: str
    result: str


def create_researcher_agent():
    """Create a researcher agent"""
    llm = get_local_llm(temperature=0.7)
    
    def researcher_node(state: AgentState):
        """Researcher agent node"""
        print(f"  [Researcher Agent] Processing task...")
        task = state.get("task", "")
        
        prompt = ChatPromptTemplate.from_template(
            "As a research agent, provide key information about: {task}"
        )
        chain = prompt | llm
        response = chain.invoke({"task": task})
        
        return {
            "messages": state.get("messages", []) + [
                {"role": "researcher", "content": response.content}
            ],
            "current_agent": "researcher",
            "result": response.content
        }
    
    return researcher_node


def create_writer_agent():
    """Create a writer agent"""
    llm = get_local_llm(temperature=0.8)
    
    def writer_node(state: AgentState):
        """Writer agent node"""
        print(f"  [Writer Agent] Creating content...")
        research = state.get("result", "")
        
        prompt = ChatPromptTemplate.from_template(
            "As a writer agent, create a well-written article based on this research: {research}"
        )
        chain = prompt | llm
        response = chain.invoke({"research": research})
        
        return {
            "messages": state.get("messages", []) + [
                {"role": "writer", "content": response.content}
            ],
            "current_agent": "writer",
            "result": response.content
        }
    
    return writer_node


def create_reviewer_agent():
    """Create a reviewer agent"""
    llm = get_local_llm(temperature=0.3)
    
    def reviewer_node(state: AgentState):
        """Reviewer agent node"""
        print(f"  [Reviewer Agent] Reviewing content...")
        content = state.get("result", "")
        
        prompt = ChatPromptTemplate.from_template(
            "As a reviewer agent, review and provide feedback on this content: {content}"
        )
        chain = prompt | llm
        response = chain.invoke({"content": content})
        
        return {
            "messages": state.get("messages", []) + [
                {"role": "reviewer", "content": response.content}
            ],
            "current_agent": "reviewer",
            "result": response.content
        }
    
    return reviewer_node


def basic_multi_agent_workflow():
    """Basic multi-agent workflow"""
    print("=" * 60)
    print("Example 1: Basic Multi-Agent Workflow")
    print("=" * 60)
    
    # Create agents
    researcher = create_researcher_agent()
    writer = create_writer_agent()
    reviewer = create_reviewer_agent()
    
    # Build graph
    workflow = StateGraph(AgentState)
    
    workflow.add_node("researcher", researcher)
    workflow.add_node("writer", writer)
    workflow.add_node("reviewer", reviewer)
    
    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", "reviewer")
    workflow.add_edge("reviewer", END)
    
    app = workflow.compile()
    
    # Execute
    initial_state = {
        "messages": [],
        "current_agent": "",
        "task": "artificial intelligence trends in 2024",
        "result": ""
    }
    
    result = app.invoke(initial_state)
    
    print("\nWorkflow completed!")
    print(f"Agents involved: {len(result['messages'])}")
    print(f"Final agent: {result['current_agent']}")
    print()


def parallel_agents_example():
    """Multiple agents working in parallel"""
    print("=" * 60)
    print("Example 2: Parallel Agent Execution")
    print("=" * 60)
    
    def tech_agent(state: AgentState):
        """Technology-focused agent"""
        print("  [Tech Agent] Analyzing technology aspects...")
        task = state.get("task", "")
        return {
            "messages": state.get("messages", []) + [
                {"role": "tech", "content": f"Tech analysis of: {task}"}
            ],
            "tech_result": f"Technology perspective on {task}"
        }
    
    def business_agent(state: AgentState):
        """Business-focused agent"""
        print("  [Business Agent] Analyzing business aspects...")
        task = state.get("task", "")
        return {
            "messages": state.get("messages", []) + [
                {"role": "business", "content": f"Business analysis of: {task}"}
            ],
            "business_result": f"Business perspective on {task}"
        }
    
    def merge_agent(state: AgentState):
        """Merge results from parallel agents"""
        print("  [Merge Agent] Combining results...")
        tech = state.get("tech_result", "")
        business = state.get("business_result", "")
        
        return {
            "messages": state.get("messages", []) + [
                {"role": "merge", "content": f"Merged: {tech} + {business}"}
            ],
            "result": f"Combined analysis: {tech} and {business}"
        }
    
    # Build graph
    workflow = StateGraph(AgentState)
    
    workflow.add_node("tech", tech_agent)
    workflow.add_node("business", business_agent)
    workflow.add_node("merge", merge_agent)
    
    workflow.set_entry_point("tech")
    workflow.add_edge("tech", "business")  # Sequential for demo
    workflow.add_edge("business", "merge")
    workflow.add_edge("merge", END)
    
    app = workflow.compile()
    
    initial_state = {
        "messages": [],
        "current_agent": "",
        "task": "cloud computing adoption",
        "result": ""
    }
    
    result = app.invoke(initial_state)
    
    print("\nParallel execution completed!")
    print(f"Messages from agents: {len(result['messages'])}")
    print()


def agent_roles_example():
    """Agents with specific roles and responsibilities"""
    print("=" * 60)
    print("Example 3: Agent Roles and Responsibilities")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.7)
    
    def data_analyst_agent(state: AgentState):
        """Data analyst agent - analyzes data"""
        print("  [Data Analyst] Analyzing data...")
        task = state.get("task", "")
        
        prompt = ChatPromptTemplate.from_template(
            "As a data analyst, what data would you need and how would you analyze: {task}"
        )
        chain = prompt | llm
        response = chain.invoke({"task": task})
        
        return {
            "messages": state.get("messages", []) + [
                {"role": "data_analyst", "content": response.content}
            ],
            "analysis": response.content
        }
    
    def developer_agent(state: AgentState):
        """Developer agent - implements solutions"""
        print("  [Developer] Implementing solution...")
        analysis = state.get("analysis", "")
        
        prompt = ChatPromptTemplate.from_template(
            "As a developer, create an implementation plan based on: {analysis}"
        )
        chain = prompt | llm
        response = chain.invoke({"analysis": analysis})
        
        return {
            "messages": state.get("messages", []) + [
                {"role": "developer", "content": response.content}
            ],
            "implementation": response.content
        }
    
    def qa_agent(state: AgentState):
        """QA agent - tests and validates"""
        print("  [QA Engineer] Testing solution...")
        implementation = state.get("implementation", "")
        
        prompt = ChatPromptTemplate.from_template(
            "As a QA engineer, what tests would you create for: {implementation}"
        )
        chain = prompt | llm
        response = chain.invoke({"implementation": implementation})
        
        return {
            "messages": state.get("messages", []) + [
                {"role": "qa", "content": response.content}
            ],
            "result": response.content
        }
    
    # Build graph
    workflow = StateGraph(AgentState)
    
    workflow.add_node("data_analyst", data_analyst_agent)
    workflow.add_node("developer", developer_agent)
    workflow.add_node("qa", qa_agent)
    
    workflow.set_entry_point("data_analyst")
    workflow.add_edge("data_analyst", "developer")
    workflow.add_edge("developer", "qa")
    workflow.add_edge("qa", END)
    
    app = workflow.compile()
    
    initial_state = {
        "messages": [],
        "current_agent": "",
        "task": "build a recommendation system",
        "result": ""
    }
    
    result = app.invoke(initial_state)
    
    print("\nRole-based workflow completed!")
    print(f"Agents: {[msg.get('role') for msg in result['messages']]}")
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
        basic_multi_agent_workflow()
        parallel_agents_example()
        agent_roles_example()
        
        print("=" * 60)
        print("All multi-agent examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

