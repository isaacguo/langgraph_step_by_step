from typing import Dict, Any, List
from .contract_definition import SafetyContract

class ContractValidator:
    def __init__(self):
        # In real implementation, these would be loaded from DB/File
        self.contracts = {
            "data_analysis": SafetyContract(
                contract_id="c_001",
                operation="analyze",
                valid_ranges={"confidence_threshold": (0.5, 1.0)},
                allowed_values={"method": ["statistical", "ml", "simple"]},
                required_permissions=["analyze_data"]
            )
        }

    def validate(self, contract_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parameters against the specified contract.
        """
        contract = self.contracts.get(contract_id)
        if not contract:
            return {"valid": False, "error": f"Contract {contract_id} not found"}

        violations = []

        # Check ranges
        for key, (min_val, max_val) in contract.valid_ranges.items():
            if key in params:
                val = params[key]
                if not (min_val <= val <= max_val):
                    violations.append(f"Value {val} for {key} out of range [{min_val}, {max_val}]")
        
        # Check allowed values
        for key, allowed in contract.allowed_values.items():
            if key in params:
                val = params[key]
                if val not in allowed:
                    violations.append(f"Value {val} for {key} not in allowed values {allowed}")

        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "contract": contract.model_dump()
        }
