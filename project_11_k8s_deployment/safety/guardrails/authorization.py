from typing import List, Dict, Any, Optional
import yaml
import os

class AuthorizationManager:
    def __init__(self, policy_path: str = "policies/auth_policy.yaml"):
        self.policy_path = policy_path
        self._load_policies()

    def _load_policies(self):
        # In a real scenario, this would load from a file or DB
        # For now, we default to a safe configuration if file doesn't exist
        self.policies = {
            "roles": {
                "user": {
                    "allowed_actions": ["read", "query", "analyze"],
                    "denied_actions": ["delete", "modify_system", "exec_code"]
                },
                "admin": {
                    "allowed_actions": ["*"],
                    "denied_actions": []
                }
            }
        }

    def check_permission(self, user_role: str, action: str, resource: str) -> bool:
        """
        Check if the user has permission to perform the action on the resource.
        """
        role_policy = self.policies["roles"].get(user_role, self.policies["roles"]["user"])
        
        # Check denied first
        if action in role_policy["denied_actions"]:
            return False
            
        # Check allowed
        if "*" in role_policy["allowed_actions"]:
            return True
            
        return action in role_policy["allowed_actions"]

    def validate_request(self, user_id: str, role: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a request against authorization rules.
        """
        is_allowed = self.check_permission(role, action, params.get("resource", "default"))
        
        return {
            "authorized": is_allowed,
            "user_id": user_id,
            "role": role,
            "action": action,
            "reason": "Authorized" if is_allowed else f"Action '{action}' not allowed for role '{role}'"
        }
