from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class UserRequest(BaseModel):
    user_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    request_id: str
    content: str
    safety_score: float
    status: str
    execution_trace: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
