import unittest
from ..safety.guardrails.authorization import AuthorizationManager
from ..safety.guardrails.policy_enforcement import PolicyEnforcementEngine

class TestGuardrails(unittest.TestCase):
    def setUp(self):
        self.auth = AuthorizationManager()
        self.policy = PolicyEnforcementEngine()

    def test_authorization(self):
        # Test allowed action
        self.assertTrue(self.auth.check_permission("user", "read", "resource1"))
        # Test denied action
        self.assertFalse(self.auth.check_permission("user", "delete", "resource1"))
        # Test admin
        self.assertTrue(self.auth.check_permission("admin", "delete", "resource1"))

    def test_policy_enforcement_regex(self):
        # Test SQL injection block
        result = self.policy.evaluate("DROP TABLE users")
        self.assertFalse(result["allowed"])
        self.assertIn("no_sql_injection", result["violations"])

        # Test safe content
        result = self.policy.evaluate("Select option A")
        self.assertTrue(result["allowed"])

if __name__ == "__main__":
    unittest.main()
