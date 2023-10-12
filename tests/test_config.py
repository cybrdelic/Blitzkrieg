import os
import unittest
from dotenv import load_dotenv
from rundbfast.config import load_configurations

class TestConfig(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Class-level setup function."""
        load_dotenv(".env.test")  # Assume you have a .env.test file for testing

    def test_default_port(self):
        """Test if DEFAULT_PORT is loaded correctly."""
        config = load_configurations()
        self.assertEqual(config.get("DEFAULT_PORT"), "5432")

    def test_timeout(self):
        """Test if TIMEOUT is loaded correctly."""
        config = load_configurations()
        self.assertEqual(config.get("TIMEOUT"), "60")

    def test_sleep_interval(self):
        """Test if SLEEP_INTERVAL is loaded correctly."""
        config = load_configurations()
        self.assertEqual(config.get("SLEEP_INTERVAL"), "2")

    @classmethod
    def tearDownClass(cls):
        """Class-level teardown function."""
        # Reset the environment variables or do other cleanup tasks.
        pass

if __name__ == "__main__":
    unittest.main()
