"""
Runtime Safety - Runtime Guardrails
Demonstrates runtime guardrails, authorization layers, and policy enforcement
"""

import os
import sys
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Literal, List, Dict, Any
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


class GuardrailState(TypedDict):
    messages: Annotated[List[Dict], "conversation messages"]
    action: str
    action_params: Dict[str, Any]
    authorization_status: str
    policy_violations: Annotated[List[str], "list of policy violations"]
    safety_score: float
    step_count: int


# Policy definitions
POLICIES = {
    "max_iterations": 10,
    "allowed_actions": ["read", "write", "analyze", "query"],
    "forbidden_keywords": ["delete", "drop", "remove", "destroy"],
    "max_file_size": 1000000,  # 1MB
    "required_permissions": {
        "write": ["write_permission"],
        "delete": ["admin_permission"]
    }
}


def action_validation_guardrail():
    """Validate actions before execution"""
    print("=" * 60)
    print("Example 1: Action Validation Guardrail")
    print("=" * 60)
    
    def validate_action_node(state: GuardrailState):
        """Validate action before execution"""
        print("  [Guardrail] Validating action...")
        action = state.get("action", "")
        action_params = state.get("action_params", {})
        violations = []
        
        # Check if action is allowed
        if action not in POLICIES["allowed_actions"]:
            violations.append(f"Action '{action}' not in allowed actions list")
        
        # Check for forbidden keywords in parameters
        params_str = str(action_params).lower()
        for keyword in POLICIES["forbidden_keywords"]:
            if keyword in params_str:
                violations.append(f"Forbidden keyword '{keyword}' detected in parameters")
        
        # Check file size if applicable
        if "file_size" in action_params:
            if action_params["file_size"] > POLICIES["max_file_size"]:
                violations.append(f"File size {action_params['file_size']} exceeds maximum")
        
        authorization_status = "approved" if len(violations) == 0 else "rejected"
        
        return {
            "authorization_status": authorization_status,
            "policy_violations": violations,
            "safety_score": 1.0 if len(violations) == 0 else max(0.0, 1.0 - len(violations) * 0.3),
            "step_count": state.get("step_count", 0) + 1
        }
    
    def execute_action_node(state: GuardrailState):
        """Execute action if authorized"""
        print("  [Executor] Executing action...")
        if state.get("authorization_status") == "approved":
            return {
                "messages": state.get("messages", []) + [
                    {"role": "system", "content": f"Action '{state.get('action')}' executed successfully"}
                ],
                "step_count": state["step_count"] + 1
            }
        else:
            return {
                "messages": state.get("messages", []) + [
                    {"role": "system", "content": f"Action blocked due to policy violations"}
                ],
                "step_count": state["step_count"] + 1
            }
    
    def route_by_authorization(state: GuardrailState) -> Literal["execute", "block"]:
        """Route based on authorization status"""
        return "execute" if state.get("authorization_status") == "approved" else "block"
    
    # Build graph
    workflow = StateGraph(GuardrailState)
    workflow.add_node("validate", validate_action_node)
    workflow.add_node("execute", execute_action_node)
    workflow.add_node("block", lambda s: {"step_count": s.get("step_count", 0) + 1})
    
    workflow.set_entry_point("validate")
    workflow.add_conditional_edges(
        "validate",
        route_by_authorization,
        {
            "execute": "execute",
            "block": "block"
        }
    )
    workflow.add_edge("execute", END)
    workflow.add_edge("block", END)
    
    app = workflow.compile()
    
    # Test cases
    test_cases = [
        {
            "messages": [],
            "action": "read",
            "action_params": {"file": "data.txt"},
            "authorization_status": "",
            "policy_violations": [],
            "safety_score": 0.0,
            "step_count": 0
        },
        {
            "messages": [],
            "action": "delete",  # Not allowed
            "action_params": {"file": "data.txt"},
            "authorization_status": "",
            "policy_violations": [],
            "safety_score": 0.0,
            "step_count": 0
        },
        {
            "messages": [],
            "action": "write",
            "action_params": {"file": "data.txt", "file_size": 2000000},  # Too large
            "authorization_status": "",
            "policy_violations": [],
            "safety_score": 0.0,
            "step_count": 0
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}: Action = {test_case['action']}")
        result = app.invoke(test_case)
        print(f"  Authorization: {result['authorization_status']}")
        if result.get("policy_violations"):
            print(f"  Violations: {result['policy_violations']}")
        print(f"  Safety Score: {result['safety_score']:.2f}")
    print()


def permission_based_authorization():
    """Permission-based authorization layer"""
    print("=" * 60)
    print("Example 2: Permission-Based Authorization")
    print("=" * 60)
    
    # User permissions
    USER_PERMISSIONS = {
        "user1": ["read", "write_permission", "analyze"],
        "user2": ["read", "analyze"],
        "admin": ["read", "write_permission", "analyze", "admin_permission"]
    }
    
    def check_permissions_node(state: GuardrailState):
        """Check user permissions"""
        print("  [Authorization] Checking permissions...")
        action = state.get("action", "")
        user_id = state.get("action_params", {}).get("user_id", "user1")
        user_perms = USER_PERMISSIONS.get(user_id, [])
        
        # Check if user has required permissions for action
        required_perms = POLICIES["required_permissions"].get(action, [])
        has_permission = all(perm in user_perms for perm in required_perms)
        
        if not has_permission:
            missing = [p for p in required_perms if p not in user_perms]
            return {
                "authorization_status": "rejected",
                "policy_violations": [f"Missing permissions: {missing}"],
                "safety_score": 0.0,
                "step_count": state.get("step_count", 0) + 1
            }
        
        return {
            "authorization_status": "approved",
            "policy_violations": [],
            "safety_score": 1.0,
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(GuardrailState)
    workflow.add_node("check_permissions", check_permissions_node)
    workflow.set_entry_point("check_permissions")
    workflow.add_edge("check_permissions", END)
    
    app = workflow.compile()
    
    # Test cases
    test_cases = [
        {
            "messages": [],
            "action": "write",
            "action_params": {"user_id": "user1", "file": "data.txt"},
            "authorization_status": "",
            "policy_violations": [],
            "safety_score": 0.0,
            "step_count": 0
        },
        {
            "messages": [],
            "action": "write",
            "action_params": {"user_id": "user2", "file": "data.txt"},  # No write permission
            "authorization_status": "",
            "policy_violations": [],
            "safety_score": 0.0,
            "step_count": 0
        },
        {
            "messages": [],
            "action": "delete",
            "action_params": {"user_id": "admin", "file": "data.txt"},
            "authorization_status": "",
            "policy_violations": [],
            "safety_score": 0.0,
            "step_count": 0
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}: User = {test_case['action_params']['user_id']}, Action = {test_case['action']}")
        result = app.invoke(test_case)
        print(f"  Authorization: {result['authorization_status']}")
        if result.get("policy_violations"):
            print(f"  Violations: {result['policy_violations']}")
    print()


def semantic_safety_check():
    """Semantic safety checks using LLM"""
    print("=" * 60)
    print("Example 3: Semantic Safety Check")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.3)
    
    def semantic_check_node(state: GuardrailState):
        """Perform semantic safety check"""
        print("  [Semantic Check] Analyzing action semantics...")
        action = state.get("action", "")
        action_params = state.get("action_params", {})
        
        prompt = ChatPromptTemplate.from_template(
            "Analyze this action for safety concerns. Respond with 'safe' or 'unsafe' followed by a brief reason.\n\n"
            "Action: {action}\n"
            "Parameters: {params}\n\n"
            "Consider: data privacy, system integrity, user safety, ethical concerns."
        )
        chain = prompt | llm
        response = chain.invoke({
            "action": action,
            "params": str(action_params)
        })
        
        result_text = response.content.lower()
        is_safe = "unsafe" not in result_text and "safe" in result_text
        
        return {
            "authorization_status": "approved" if is_safe else "rejected",
            "policy_violations": [] if is_safe else [f"Semantic check: {response.content}"],
            "safety_score": 1.0 if is_safe else 0.5,
            "messages": state.get("messages", []) + [
                {"role": "safety_checker", "content": response.content}
            ],
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(GuardrailState)
    workflow.add_node("semantic_check", semantic_check_node)
    workflow.set_entry_point("semantic_check")
    workflow.add_edge("semantic_check", END)
    
    app = workflow.compile()
    
    # Test case
    test_case = {
        "messages": [],
        "action": "analyze",
        "action_params": {"data": "user analytics", "scope": "public"},
        "authorization_status": "",
        "policy_violations": [],
        "safety_score": 0.0,
        "step_count": 0
    }
    
    print("\nTesting semantic safety check...")
    result = app.invoke(test_case)
    print(f"  Authorization: {result['authorization_status']}")
    print(f"  Safety Score: {result['safety_score']:.2f}")
    if result.get("messages"):
        print(f"  Check Result: {result['messages'][-1].get('content', '')[:100]}")
    print()


def multi_layer_guardrails():
    """Multiple guardrail layers"""
    print("=" * 60)
    print("Example 4: Multi-Layer Guardrails")
    print("=" * 60)
    
    def policy_check_node(state: GuardrailState):
        """Layer 1: Policy check"""
        print("  [Layer 1: Policy] Checking policies...")
        action = state.get("action", "")
        violations = []
        
        if action not in POLICIES["allowed_actions"]:
            violations.append("Action not allowed")
        
        return {
            "policy_violations": violations,
            "step_count": state.get("step_count", 0) + 1
        }
    
    def permission_check_node(state: GuardrailState):
        """Layer 2: Permission check"""
        print("  [Layer 2: Permissions] Checking permissions...")
        # Simplified permission check
        has_permission = len(state.get("policy_violations", [])) == 0
        return {
            "authorization_status": "approved" if has_permission else "rejected",
            "step_count": state["step_count"] + 1
        }
    
    def safety_score_node(state: GuardrailState):
        """Layer 3: Safety scoring"""
        print("  [Layer 3: Safety Score] Calculating safety score...")
        violations = len(state.get("policy_violations", []))
        score = max(0.0, 1.0 - violations * 0.3)
        return {
            "safety_score": score,
            "step_count": state["step_count"] + 1
        }
    
    workflow = StateGraph(GuardrailState)
    workflow.add_node("policy_check", policy_check_node)
    workflow.add_node("permission_check", permission_check_node)
    workflow.add_node("safety_score", safety_score_node)
    
    workflow.set_entry_point("policy_check")
    workflow.add_edge("policy_check", "permission_check")
    workflow.add_edge("permission_check", "safety_score")
    workflow.add_edge("safety_score", END)
    
    app = workflow.compile()
    
    test_case = {
        "messages": [],
        "action": "read",
        "action_params": {},
        "authorization_status": "",
        "policy_violations": [],
        "safety_score": 0.0,
        "step_count": 0
    }
    
    result = app.invoke(test_case)
    print(f"\nMulti-layer guardrail result:")
    print(f"  Authorization: {result['authorization_status']}")
    print(f"  Safety Score: {result['safety_score']:.2f}")
    print(f"  Total Steps: {result['step_count']}")
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
        print("Note: Some examples will work without server, but semantic checks require it.")
    
    try:
        action_validation_guardrail()
        permission_based_authorization()
        semantic_safety_check()
        multi_layer_guardrails()
        
        print("=" * 60)
        print("All runtime guardrail examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

