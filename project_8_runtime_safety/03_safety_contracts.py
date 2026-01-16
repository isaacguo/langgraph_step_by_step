"""
Runtime Safety - Safety Contracts
Demonstrates structured safety contracts, operating ranges, and escalation paths
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Dict, Any, List, Literal, Optional
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field, field_validator, validator

# Load environment variables
load_dotenv()


# Safety Contract Definitions
class SafetyContract(BaseModel):
    """Safety contract definition"""
    contract_id: str
    operation: str
    valid_ranges: Dict[str, tuple]  # e.g., {"temperature": (0, 100)}
    required_permissions: List[str]
    max_execution_time: float
    escalation_path: List[str]
    rollback_required: bool = True
    
    @field_validator('valid_ranges')
    def validate_ranges(cls, v):
        """Ensure ranges are valid tuples"""
        for key, value in v.items():
            if not isinstance(value, tuple) or len(value) != 2:
                raise ValueError(f"Range for {key} must be a tuple of (min, max)")
            if value[0] >= value[1]:
                raise ValueError(f"Range for {key} must have min < max")
        return v


class ContractState(TypedDict):
    operation: str
    parameters: Dict[str, Any]
    active_contract: Optional[SafetyContract]
    contract_violations: Annotated[List[str], "list of contract violations"]
    escalation_level: int
    safety_score: float
    step_count: int


# Predefined safety contracts
SAFETY_CONTRACTS = {
    "data_read": SafetyContract(
        contract_id="data_read",
        operation="read",
        valid_ranges={"file_size": (0, 10000000)},  # 10MB max
        required_permissions=["read_permission"],
        max_execution_time=30.0,
        escalation_path=["warn", "block"],
        rollback_required=False
    ),
    "data_write": SafetyContract(
        contract_id="data_write",
        operation="write",
        valid_ranges={"file_size": (0, 5000000)},  # 5MB max
        required_permissions=["write_permission"],
        max_execution_time=60.0,
        escalation_path=["warn", "require_approval", "block"],
        rollback_required=True
    ),
    "data_delete": SafetyContract(
        contract_id="data_delete",
        operation="delete",
        valid_ranges={},
        required_permissions=["admin_permission"],
        max_execution_time=10.0,
        escalation_path=["require_approval", "block"],
        rollback_required=True
    )
}


def contract_definition_example():
    """Define and validate safety contracts"""
    print("=" * 60)
    print("Example 1: Safety Contract Definition")
    print("=" * 60)
    
    def load_contract_node(state: ContractState):
        """Load appropriate safety contract"""
        print("  [Contract Loader] Loading safety contract...")
        operation = state.get("operation", "")
        
        # Find matching contract
        contract = None
        for contract_id, contract_def in SAFETY_CONTRACTS.items():
            if contract_def.operation == operation:
                contract = contract_def
                break
        
        if not contract:
            return {
                "active_contract": None,
                "contract_violations": [f"No contract found for operation '{operation}'"],
                "step_count": state.get("step_count", 0) + 1
            }
        
        return {
            "active_contract": contract,
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(ContractState)
    workflow.add_node("load_contract", load_contract_node)
    workflow.set_entry_point("load_contract")
    workflow.add_edge("load_contract", END)
    
    app = workflow.compile()
    
    test_cases = [
        {
            "operation": "read",
            "parameters": {},
            "active_contract": None,
            "contract_violations": [],
            "escalation_level": 0,
            "safety_score": 0.0,
            "step_count": 0
        },
        {
            "operation": "write",
            "parameters": {},
            "active_contract": None,
            "contract_violations": [],
            "escalation_level": 0,
            "safety_score": 0.0,
            "step_count": 0
        },
        {
            "operation": "unknown",
            "parameters": {},
            "active_contract": None,
            "contract_violations": [],
            "escalation_level": 0,
            "safety_score": 0.0,
            "step_count": 0
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}: Operation = {test_case['operation']}")
        result = app.invoke(test_case)
        if result.get("active_contract"):
            contract = result["active_contract"]
            print(f"  Contract ID: {contract.contract_id}")
            print(f"  Max execution time: {contract.max_execution_time}s")
            print(f"  Rollback required: {contract.rollback_required}")
        else:
            print(f"  No contract found")
            if result.get("contract_violations"):
                print(f"  Violations: {result['contract_violations']}")
    print()


def operating_range_validation():
    """Validate parameters against operating ranges"""
    print("=" * 60)
    print("Example 2: Operating Range Validation")
    print("=" * 60)
    
    def validate_ranges_node(state: ContractState):
        """Validate parameters against contract ranges"""
        print("  [Range Validator] Validating operating ranges...")
        contract = state.get("active_contract")
        parameters = state.get("parameters", {})
        violations = []
        
        if not contract:
            return {
                "contract_violations": ["No contract active"],
                "step_count": state.get("step_count", 0) + 1
            }
        
        # Check each parameter against valid ranges
        for param_name, (min_val, max_val) in contract.valid_ranges.items():
            if param_name in parameters:
                param_value = parameters[param_name]
                if param_value < min_val or param_value > max_val:
                    violations.append(
                        f"Parameter '{param_name}' value {param_value} outside range [{min_val}, {max_val}]"
                    )
        
        return {
            "contract_violations": violations,
            "safety_score": 1.0 if len(violations) == 0 else max(0.0, 1.0 - len(violations) * 0.3),
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(ContractState)
    workflow.add_node("validate_ranges", validate_ranges_node)
    workflow.set_entry_point("validate_ranges")
    workflow.add_edge("validate_ranges", END)
    
    app = workflow.compile()
    
    # Load contract first
    contract = SAFETY_CONTRACTS["data_read"]
    
    test_cases = [
        {
            "operation": "read",
            "parameters": {"file_size": 5000000},  # Within range
            "active_contract": contract,
            "contract_violations": [],
            "escalation_level": 0,
            "safety_score": 0.0,
            "step_count": 0
        },
        {
            "operation": "read",
            "parameters": {"file_size": 15000000},  # Outside range
            "active_contract": contract,
            "contract_violations": [],
            "escalation_level": 0,
            "safety_score": 0.0,
            "step_count": 0
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}: file_size = {test_case['parameters'].get('file_size')}")
        result = app.invoke(test_case)
        print(f"  Violations: {len(result['contract_violations'])}")
        if result.get("contract_violations"):
            for violation in result["contract_violations"]:
                print(f"    - {violation}")
        print(f"  Safety Score: {result['safety_score']:.2f}")
    print()


def escalation_path_management():
    """Manage escalation paths based on contract violations"""
    print("=" * 60)
    print("Example 3: Escalation Path Management")
    print("=" * 60)
    
    def escalate_node(state: ContractState):
        """Handle escalation based on violations"""
        print("  [Escalation Handler] Processing escalation...")
        contract = state.get("active_contract")
        violations = state.get("contract_violations", [])
        current_level = state.get("escalation_level", 0)
        
        if not contract:
            return {
                "escalation_level": 0,
                "step_count": state.get("step_count", 0) + 1
            }
        
        # Determine escalation level based on violations
        if len(violations) == 0:
            escalation_level = 0
        elif len(violations) == 1:
            escalation_level = 1  # First level: warn
        else:
            escalation_level = min(len(violations), len(contract.escalation_path))
        
        # Get escalation action
        if escalation_level > 0 and escalation_level <= len(contract.escalation_path):
            escalation_action = contract.escalation_path[escalation_level - 1]
        else:
            escalation_action = "none"
        
        return {
            "escalation_level": escalation_level,
            "messages": state.get("messages", []) + [
                {"role": "escalation", "content": f"Escalation: {escalation_action}"}
            ] if escalation_action != "none" else state.get("messages", []),
            "step_count": state.get("step_count", 0) + 1
        }
    
    def warn_node(state: ContractState):
        """Warning level escalation"""
        print("  [Warning] Issuing warning...")
        return {
            "messages": state.get("messages", []) + [
                {"role": "system", "content": "WARNING: Contract violation detected"}
            ],
            "step_count": state["step_count"] + 1
        }
    
    def require_approval_node(state: ContractState):
        """Require approval escalation"""
        print("  [Approval] Requiring approval...")
        return {
            "messages": state.get("messages", []) + [
                {"role": "system", "content": "APPROVAL REQUIRED: Operation needs manual approval"}
            ],
            "step_count": state["step_count"] + 1
        }
    
    def block_node(state: ContractState):
        """Block operation escalation"""
        print("  [Block] Blocking operation...")
        return {
            "messages": state.get("messages", []) + [
                {"role": "system", "content": "BLOCKED: Operation blocked due to contract violations"}
            ],
            "step_count": state["step_count"] + 1
        }
    
    def route_escalation(state: ContractState) -> Literal["warn", "require_approval", "block", "continue"]:
        """Route based on escalation level"""
        level = state.get("escalation_level", 0)
        contract = state.get("active_contract")
        
        if level == 0:
            return "continue"
        elif not contract:
            return "continue"
        elif level <= len(contract.escalation_path):
            action = contract.escalation_path[level - 1]
            if action == "warn":
                return "warn"
            elif action == "require_approval":
                return "require_approval"
            elif action == "block":
                return "block"
        
        return "continue"
    
    workflow = StateGraph(ContractState)
    workflow.add_node("escalate", escalate_node)
    workflow.add_node("warn", warn_node)
    workflow.add_node("require_approval", require_approval_node)
    workflow.add_node("block", block_node)
    
    workflow.set_entry_point("escalate")
    workflow.add_conditional_edges(
        "escalate",
        route_escalation,
        {
            "warn": "warn",
            "require_approval": "require_approval",
            "block": "block",
            "continue": END
        }
    )
    workflow.add_edge("warn", END)
    workflow.add_edge("require_approval", END)
    workflow.add_edge("block", END)
    
    app = workflow.compile()
    
    contract = SAFETY_CONTRACTS["data_write"]
    
    test_cases = [
        {
            "operation": "write",
            "parameters": {},
            "active_contract": contract,
            "contract_violations": [],
            "escalation_level": 0,
            "safety_score": 1.0,
            "step_count": 0
        },
        {
            "operation": "write",
            "parameters": {},
            "active_contract": contract,
            "contract_violations": ["Parameter violation"],
            "escalation_level": 0,
            "safety_score": 0.7,
            "step_count": 0
        },
        {
            "operation": "write",
            "parameters": {},
            "active_contract": contract,
            "contract_violations": ["Violation 1", "Violation 2"],
            "escalation_level": 0,
            "safety_score": 0.4,
            "step_count": 0
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}: {len(test_case['contract_violations'])} violations")
        result = app.invoke(test_case)
        print(f"  Escalation level: {result['escalation_level']}")
        if result.get("messages"):
            print(f"  Action: {result['messages'][-1].get('content', '')}")
    print()


def contract_enforcement_in_graph():
    """Enforce contracts in graph execution flow"""
    print("=" * 60)
    print("Example 4: Contract Enforcement in Graph Flow")
    print("=" * 60)
    
    def load_and_validate_node(state: ContractState):
        """Load contract and validate"""
        print("  [Contract Enforcement] Loading and validating contract...")
        operation = state.get("operation", "")
        
        # Load contract
        contract = None
        for contract_def in SAFETY_CONTRACTS.values():
            if contract_def.operation == operation:
                contract = contract_def
                break
        
        if not contract:
            return {
                "active_contract": None,
                "contract_violations": ["No contract found"],
                "step_count": state.get("step_count", 0) + 1
            }
        
        # Validate parameters
        parameters = state.get("parameters", {})
        violations = []
        for param_name, (min_val, max_val) in contract.valid_ranges.items():
            if param_name in parameters:
                param_value = parameters[param_name]
                if param_value < min_val or param_value > max_val:
                    violations.append(f"{param_name} out of range")
        
        return {
            "active_contract": contract,
            "contract_violations": violations,
            "safety_score": 1.0 if len(violations) == 0 else 0.5,
            "step_count": state.get("step_count", 0) + 1
        }
    
    def execute_with_contract_node(state: ContractState):
        """Execute operation with contract enforcement"""
        print("  [Execution] Executing with contract enforcement...")
        violations = state.get("contract_violations", [])
        
        if len(violations) > 0:
            return {
                "messages": state.get("messages", []) + [
                    {"role": "system", "content": f"Execution blocked: {len(violations)} violations"}
                ],
                "step_count": state["step_count"] + 1
            }
        
        return {
            "messages": state.get("messages", []) + [
                {"role": "system", "content": "Execution allowed: Contract satisfied"}
            ],
            "step_count": state["step_count"] + 1
        }
    
    workflow = StateGraph(ContractState)
    workflow.add_node("load_validate", load_and_validate_node)
    workflow.add_node("execute", execute_with_contract_node)
    
    workflow.set_entry_point("load_validate")
    workflow.add_edge("load_validate", "execute")
    workflow.add_edge("execute", END)
    
    app = workflow.compile()
    
    test_case = {
        "operation": "read",
        "parameters": {"file_size": 5000000},
        "active_contract": None,
        "contract_violations": [],
        "escalation_level": 0,
        "safety_score": 0.0,
        "step_count": 0
    }
    
    result = app.invoke(test_case)
    print(f"\nExecution result:")
    if result.get("messages"):
        print(f"  {result['messages'][-1].get('content', '')}")
    print(f"  Safety Score: {result['safety_score']:.2f}")
    print()


if __name__ == "__main__":
    try:
        contract_definition_example()
        operating_range_validation()
        escalation_path_management()
        contract_enforcement_in_graph()
        
        print("=" * 60)
        print("All safety contract examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

