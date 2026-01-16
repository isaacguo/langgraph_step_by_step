from fastapi import APIRouter
from typing import Dict, Any, List
from datetime import datetime

router = APIRouter(prefix="/introspection", tags=["introspection"])

# Mock database for decisions (replace with real DB access)
decision_history = []

@router.get("/decisions")
async def get_decisions(limit: int = 10):
    return decision_history[-limit:]

@router.get("/decisions/{decision_id}")
async def get_decision(decision_id: str):
    for d in decision_history:
        if d["id"] == decision_id:
            return d
    return {"error": "Decision not found"}

def record_decision(decision_id: str, context: Dict[str, Any], result: str, rationale: str):
    decision_history.append({
        "id": decision_id,
        "timestamp": datetime.now().isoformat(),
        "context": context,
        "result": result,
        "rationale": rationale
    })
