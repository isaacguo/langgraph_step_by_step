import re
from typing import Dict, Any, List

class PromptSafety:
    def __init__(self):
        self.injection_patterns = [
            r"(?i)ignore previous instructions",
            r"(?i)system override",
            r"(?i)sudo mode",
            r"(?i)developer mode",
            r"(?i)jailbreak",
            r"(?i)DAN mode"
        ]

    def check_injection(self, prompt: str) -> Dict[str, Any]:
        """
        Check for prompt injection attempts.
        """
        detected_patterns = []
        for pattern in self.injection_patterns:
            if re.search(pattern, prompt):
                detected_patterns.append(pattern)
        
        return {
            "safe": len(detected_patterns) == 0,
            "detected_patterns": detected_patterns
        }

    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Comprehensive prompt validation.
        """
        injection_check = self.check_injection(prompt)
        
        if not injection_check["safe"]:
            return {
                "valid": False,
                "reason": "Prompt injection detected",
                "details": injection_check
            }
            
        # Check length
        if len(prompt) > 4000:
            return {
                "valid": False,
                "reason": "Prompt too long"
            }
            
        return {"valid": True, "reason": "Safe"}
