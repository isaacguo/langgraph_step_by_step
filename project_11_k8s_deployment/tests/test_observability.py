import unittest
from ..safety.observability.logger import configure_logging

class TestObservability(unittest.TestCase):
    def test_logger_config(self):
        log = configure_logging()
        self.assertIsNotNone(log)

if __name__ == "__main__":
    unittest.main()
