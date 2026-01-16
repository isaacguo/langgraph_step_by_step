from typing import List, Dict, Any, Tuple, Optional
from pydantic import BaseModel, Field, field_validator

class SafetyContract(BaseModel):
    """
    Defines the safety contract for an operation.
    """
    contract_id: str
    operation: str
    valid_ranges: Dict[str, Tuple[float, float]] = Field(default_factory=dict)
    allowed_values: Dict[str, List[Any]] = Field(default_factory=dict)
    required_permissions: List[str] = Field(default_factory=list)
    max_execution_time: float = 30.0
    requires_approval: bool = False
    
    @field_validator('valid_ranges')
    @classmethod
    def validate_ranges(cls, v):
        for key, val in v.items():
            if len(val) != 2 or val[0] > val[1]:
                raise ValueError(f"Invalid range for {key}: {val}")
        return v
