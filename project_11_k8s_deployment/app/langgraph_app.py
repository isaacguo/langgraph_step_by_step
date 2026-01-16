from typing import TypedDict, Annotated, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .config import settings
from safety.integration.langgraph_integration import safety_check_node

# Define the state
class AgentState(TypedDict):
    messages: List[Dict[str, Any]]
    user_input: str
    user_id: str
    safety_status: str
    parsed_intent: Dict[str, Any]
    processing_result: str
    errors: List[str]

# Define the processing node
def process_node(state: AgentState):
    """
    Process the user input using the LLM.
    """
    messages = state.get("messages", [])
    user_input = state.get("user_input", "")
    
    # Initialize LLM
    llm = ChatOpenAI(
        base_url=settings.LM_STUDIO_BASE_URL,
        model=settings.LM_STUDIO_MODEL,
        api_key=settings.LM_STUDIO_API_KEY,
        temperature=0.7
    )
    
    try:
        # Simple interaction
        response = llm.invoke([
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=user_input)
        ])
        
        return {
            "processing_result": response.content,
            "messages": messages + [{"role": "assistant", "content": response.content}]
        }
    except Exception as e:
        return {
            "errors": state.get("errors", []) + [str(e)],
            "safety_status": "error"
        }

def route_safety(state: AgentState) -> Literal["process", "block"]:
    if state.get("safety_status") == "approved":
        return "process"
    return "block"

def block_node(state: AgentState):
    return {
        "processing_result": "Request blocked by safety system.",
        "safety_status": "blocked"
    }

# Create the graph
def create_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("safety_check", safety_check_node)
    workflow.add_node("process", process_node)
    workflow.add_node("block", block_node)
    
    workflow.set_entry_point("safety_check")
    
    workflow.add_conditional_edges(
        "safety_check",
        route_safety,
        {
            "process": "process",
            "block": "block"
        }
    )
    
    workflow.add_edge("process", END)
    workflow.add_edge("block", END)
    
    return workflow.compile()
