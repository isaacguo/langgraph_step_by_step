from typing import Dict, Any, Optional
from ..guardrails.authorization import AuthorizationManager
from ..intent.intent_parser import IntentParser
from ..intent.prompt_safety import PromptSafety
from ..observability.logger import logger
from ..observability.telemetry_collector import TelemetryCollector
from ..anomaly.safety_gate import SafetyGate

class SafetyOrchestrator:
    def __init__(self):
        self.auth_manager = AuthorizationManager()
        self.intent_parser = IntentParser()
        self.prompt_safety = PromptSafety()
        self.telemetry = TelemetryCollector()
        self.safety_gate = SafetyGate()

    def validate_input(self, user_id: str, user_input: str) -> Dict[str, Any]:
        """
        Orchestrate input validation.
        """
        # 1. Prompt Safety
        prompt_check = self.prompt_safety.validate_prompt(user_input)
        if not prompt_check["valid"]:
            self.telemetry.collect("safety_violation", {"type": "prompt_injection", "user_id": user_id})
            return {"valid": False, "error": prompt_check["reason"]}

        # 2. Intent Parsing
        intent = self.intent_parser.parse(user_input)
        
        # 3. Authorization
        # Assuming 'user' role for now
        auth_check = self.auth_manager.validate_request(
            user_id=user_id,
            role="user",
            action=intent.get("action", "unknown"),
            params=intent.get("params", {})
        )
        
        if not auth_check["authorized"]:
             self.telemetry.collect("safety_violation", {"type": "unauthorized", "user_id": user_id})
             return {"valid": False, "error": auth_check["reason"]}

        return {"valid": True, "intent": intent}
