import unittest
from ..safety.recovery.checkpoint_manager import CheckpointManager

class TestRecovery(unittest.TestCase):
    def test_checkpoint_init(self):
        # Use in-memory DB for test
        cm = CheckpointManager(":memory:")
        self.assertIsNotNone(cm.get_checkpointer())

if __name__ == "__main__":
    unittest.main()
