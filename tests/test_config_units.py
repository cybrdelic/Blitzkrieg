import os
import unittest
from unittest.mock import patch
from dotenv import load_dotenv
from rundbfast.config import load_configurations

class TestConfig(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Class-level setup function."""
        load_dotenv(".env.test")

    @patch('os.getenv')
    def test_default_port(self, mock_getenv):
        """Test if DEFAULT_PORT is loaded correctly."""
        mock_getenv.return_value = "5432"
        config = load_configurations()
        self.assertEqual(config.get("DEFAULT_PORT"), "5432")

    @patch('os.getenv')
    def test_timeout(self, mock_getenv):
        """Test if TIMEOUT is loaded correctly."""
        mock_getenv.return_value = "60"
        config = load_configurations()
        self.assertEqual(config.get("TIMEOUT"), "60")

    @patch('os.getenv')
    def test_sleep_interval(self, mock_getenv):
        """Test if SLEEP_INTERVAL is loaded correctly."""
        mock_getenv.return_value = "2"
        config = load_configurations()
        self.assertEqual(config.get("SLEEP_INTERVAL"), "2")

    @classmethod
    def tearDownClass(cls):
        """Class-level teardown function."""
        pass

if __name__ == "__main__":
    unittest.main()
