"""
LangGraph Basics - Conditional Edges
Demonstrates conditional routing and decision making in graphs
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

# Define state schema
class GraphState(TypedDict):
    messages: Annotated[list, "list of messages"]
    user_input: str
    decision: str
    step_count: int


def simple_conditional_routing():
    """Simple conditional routing based on state"""
    print("=" * 60)
    print("Example 1: Simple Conditional Routing")
    print("=" * 60)
    
    def start_node(state: GraphState):
        """Start node"""
        print("Executing: start_node")
        return {"step_count": state.get("step_count", 0) + 1}
    
    def process_a(state: GraphState):
        """Process path A"""
        print("Executing: process_a (Path A)")
        return {
            "messages": state.get("messages", []) + [{"content": "Took path A"}],
            "step_count": state["step_count"] + 1
        }
    
    def process_b(state: GraphState):
        """Process path B"""
        print("Executing: process_b (Path B)")
        return {
            "messages": state.get("messages", []) + [{"content": "Took path B"}],
            "step_count": state["step_count"] + 1
        }
    
    def route_decision(state: GraphState) -> Literal["path_a", "path_b"]:
        """Route based on user input length"""
        user_input = state.get("user_input", "")
        if len(user_input) > 10:
            return "path_a"
        else:
            return "path_b"
    
    # Build graph
    workflow = StateGraph(GraphState)
    
    workflow.add_node("start", start_node)
    workflow.add_node("process_a", process_a)
    workflow.add_node("process_b", process_b)
    
    workflow.set_entry_point("start")
    workflow.add_conditional_edges(
        "start",
        route_decision,
        {
            "path_a": "process_a",
            "path_b": "process_b"
        }
    )
    workflow.add_edge("process_a", END)
    workflow.add_edge("process_b", END)
    
    app = workflow.compile()
    
    # Test with different inputs
    test_cases = [
        {"user_input": "short", "messages": [], "step_count": 0},
        {"user_input": "this is a longer input string", "messages": [], "step_count": 0}
    ]
    
    for test_case in test_cases:
        print(f"\nTesting with input: '{test_case['user_input']}'")
        result = app.invoke(test_case)
        print(f"Decision: {result.get('messages', [{}])[-1].get('content', '')}")
    print()


def llm_based_routing():
    """Use LLM to make routing decisions"""
    print("=" * 60)
    print("Example 2: LLM-Based Routing")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.3)
    
    def classify_intent(state: GraphState):
        """Classify user intent"""
        print("Executing: classify_intent")
        user_input = state.get("user_input", "")
        
        prompt = ChatPromptTemplate.from_template(
            "Classify this user query as either 'question', 'complaint', or 'compliment'. "
            "Respond with only one word: question, complaint, or compliment.\n\n"
            "Query: {query}"
        )
        chain = prompt | llm
        response = chain.invoke({"query": user_input})
        
        intent = response.content.strip().lower()
        return {
            "decision": intent,
            "step_count": state.get("step_count", 0) + 1
        }
    
    def handle_question(state: GraphState):
        """Handle question intent"""
        print("Executing: handle_question")
        llm = get_local_llm(temperature=0.7)
        user_input = state.get("user_input", "")
        
        prompt = ChatPromptTemplate.from_template(
            "Answer this question helpfully: {question}"
        )
        chain = prompt | llm
        response = chain.invoke({"question": user_input})
        
        return {
            "messages": state.get("messages", []) + [
                {"role": "assistant", "content": f"Answer: {response.content}"}
            ],
            "step_count": state["step_count"] + 1
        }
    
    def handle_complaint(state: GraphState):
        """Handle complaint intent"""
        print("Executing: handle_complaint")
        return {
            "messages": state.get("messages", []) + [
                {"role": "assistant", "content": "I'm sorry to hear that. Let me help resolve this issue."}
            ],
            "step_count": state["step_count"] + 1
        }
    
    def handle_compliment(state: GraphState):
        """Handle compliment intent"""
        print("Executing: handle_compliment")
        return {
            "messages": state.get("messages", []) + [
                {"role": "assistant", "content": "Thank you so much! I'm glad I could help."}
            ],
            "step_count": state["step_count"] + 1
        }
    
    def route_by_intent(state: GraphState) -> Literal["question", "complaint", "compliment"]:
        """Route based on classified intent"""
        intent = state.get("decision", "question")
        # Normalize to ensure it matches our edges
        if "complaint" in intent:
            return "complaint"
        elif "compliment" in intent:
            return "compliment"
        else:
            return "question"
    
    # Build graph
    workflow = StateGraph(GraphState)
    
    workflow.add_node("classify", classify_intent)
    workflow.add_node("question", handle_question)
    workflow.add_node("complaint", handle_complaint)
    workflow.add_node("compliment", handle_compliment)
    
    workflow.set_entry_point("classify")
    workflow.add_conditional_edges(
        "classify",
        route_by_intent,
        {
            "question": "question",
            "complaint": "complaint",
            "compliment": "compliment"
        }
    )
    workflow.add_edge("question", END)
    workflow.add_edge("complaint", END)
    workflow.add_edge("compliment", END)
    
    app = workflow.compile()
    
    # Test with different intents
    test_cases = [
        {"user_input": "What is the weather today?", "messages": [], "step_count": 0},
        {"user_input": "This service is terrible!", "messages": [], "step_count": 0},
        {"user_input": "You're doing a great job!", "messages": [], "step_count": 0}
    ]
    
    for test_case in test_cases:
        print(f"\nInput: '{test_case['user_input']}'")
        result = app.invoke(test_case)
        print(f"Intent: {result.get('decision', 'unknown')}")
        if result.get("messages"):
            print(f"Response: {result['messages'][-1].get('content', '')[:100]}")
    print()


def multi_condition_routing():
    """Complex routing with multiple conditions"""
    print("=" * 60)
    print("Example 3: Multi-Condition Routing")
    print("=" * 60)
    
    def analyze_input(state: GraphState):
        """Analyze input and set multiple flags"""
        print("Executing: analyze_input")
        user_input = state.get("user_input", "").lower()
        
        # Simple keyword-based analysis
        is_urgent = any(word in user_input for word in ["urgent", "asap", "immediately", "emergency"])
        needs_info = any(word in user_input for word in ["what", "how", "why", "when", "where"])
        is_action = any(word in user_input for word in ["do", "create", "make", "send", "delete"])
        
        return {
            "is_urgent": is_urgent,
            "needs_info": needs_info,
            "is_action": is_action,
            "step_count": state.get("step_count", 0) + 1
        }
    
    def handle_urgent(state: GraphState):
        """Handle urgent requests"""
        print("Executing: handle_urgent")
        return {
            "messages": state.get("messages", []) + [{"content": "Handling urgent request with priority"}],
            "step_count": state["step_count"] + 1
        }
    
    def handle_info_request(state: GraphState):
        """Handle information requests"""
        print("Executing: handle_info_request")
        return {
            "messages": state.get("messages", []) + [{"content": "Providing information"}],
            "step_count": state["step_count"] + 1
        }
    
    def handle_action(state: GraphState):
        """Handle action requests"""
        print("Executing: handle_action")
        return {
            "messages": state.get("messages", []) + [{"content": "Executing action"}],
            "step_count": state["step_count"] + 1
        }
    
    def route_complex(state: GraphState) -> Literal["urgent", "info", "action", "default"]:
        """Complex routing logic"""
        if state.get("is_urgent", False):
            return "urgent"
        elif state.get("needs_info", False):
            return "info"
        elif state.get("is_action", False):
            return "action"
        else:
            return "default"
    
    # Build graph
    workflow = StateGraph(GraphState)
    
    workflow.add_node("analyze", analyze_input)
    workflow.add_node("urgent", handle_urgent)
    workflow.add_node("info", handle_info_request)
    workflow.add_node("action", handle_action)
    
    workflow.set_entry_point("analyze")
    workflow.add_conditional_edges(
        "analyze",
        route_complex,
        {
            "urgent": "urgent",
            "info": "info",
            "action": "action",
            "default": END
        }
    )
    workflow.add_edge("urgent", END)
    workflow.add_edge("info", END)
    workflow.add_edge("action", END)
    
    app = workflow.compile()
    
    # Test cases
    test_cases = [
        {"user_input": "URGENT: Need help immediately!", "messages": [], "step_count": 0},
        {"user_input": "What is the status?", "messages": [], "step_count": 0},
        {"user_input": "Please create a new file", "messages": [], "step_count": 0},
        {"user_input": "Hello there", "messages": [], "step_count": 0}
    ]
    
    for test_case in test_cases:
        print(f"\nInput: '{test_case['user_input']}'")
        result = app.invoke(test_case)
        if result.get("messages"):
            print(f"Result: {result['messages'][-1].get('content', '')}")
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
        simple_conditional_routing()
        llm_based_routing()
        multi_condition_routing()
        
        print("=" * 60)
        print("All conditional edge examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

