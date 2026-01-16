from typing import Dict, Any, Callable
from .safety_orchestrator import SafetyOrchestrator

orchestrator = SafetyOrchestrator()

def safety_check_node(state: Dict[str, Any]):
    """
    LangGraph node for initial safety checks.
    """
    user_input = state.get("user_input", "")
    user_id = state.get("user_id", "anonymous")
    
    result = orchestrator.validate_input(user_id, user_input)
    
    if not result["valid"]:
        return {
            "safety_status": "blocked",
            "errors": [result["error"]]
        }
        
    return {
        "safety_status": "approved",
        "parsed_intent": result["intent"]
    }
