from typing import Dict, Any, List
import yaml
import re

class PolicyEnforcementEngine:
    def __init__(self):
        self.policies = self._load_policies()

    def _load_policies(self):
        return [
            {
                "name": "no_sql_injection",
                "pattern": r"(?i)(drop|delete|update|insert).*table",
                "type": "regex",
                "action": "block"
            },
            {
                "name": "max_length",
                "rule": lambda x: len(str(x)) <= 1000,
                "type": "lambda",
                "action": "truncate"
            }
        ]

    def evaluate(self, content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluate content against policies.
        """
        violations = []
        modified_content = content
        
        for policy in self.policies:
            if policy["type"] == "regex":
                if re.search(policy["pattern"], modified_content):
                    violations.append(policy["name"])
                    if policy["action"] == "block":
                        return {"allowed": False, "violations": violations, "content": content}
            
            elif policy["type"] == "lambda":
                if not policy["rule"](modified_content):
                    violations.append(policy["name"])
                    if policy["action"] == "truncate":
                        modified_content = modified_content[:1000]

        return {
            "allowed": len(violations) == 0 or all(p.get("action") != "block" for p in self.policies if p["name"] in violations),
            "violations": violations,
            "content": modified_content
        }
