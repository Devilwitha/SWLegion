import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os

# Adjust path so we can import utilities
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utilities.LegionUtils import get_gemini_key


class TestGeminiKeyRetrieval(unittest.TestCase):
    """Test suite for Gemini API key handling."""

    @patch('utilities.LegionUtils.os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='test-api-key-12345')
    def test_get_gemini_key_valid(self, mock_file, mock_exists):
        """Test retrieving a valid Gemini API key."""
        key = get_gemini_key("gemini_key.txt")
        self.assertEqual(key, "test-api-key-12345")

    @patch('utilities.LegionUtils.os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='BITTE_HIER_API_KEY_EINFUEGEN')
    def test_get_gemini_key_placeholder(self, mock_file, mock_exists):
        """Test that placeholder text returns None."""
        key = get_gemini_key("gemini_key.txt")
        self.assertIsNone(key)

    @patch('utilities.LegionUtils.os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='')
    def test_get_gemini_key_empty(self, mock_file, mock_exists):
        """Test that empty file returns None."""
        key = get_gemini_key("gemini_key.txt")
        self.assertIsNone(key)

    @patch('utilities.LegionUtils.os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open)
    def test_get_gemini_key_file_not_exists_creates_placeholder(self, mock_file, mock_exists):
        """Test that missing file creates a placeholder and returns None."""
        key = get_gemini_key("gemini_key.txt")
        self.assertIsNone(key)
        # Verify file was written
        mock_file.assert_called()

    @patch('utilities.LegionUtils.os.path.exists', return_value=True)
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_get_gemini_key_read_error(self, mock_file, mock_exists):
        """Test handling of file read errors."""
        key = get_gemini_key("gemini_key.txt")
        self.assertIsNone(key)

    @patch('utilities.LegionUtils.os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='   AIzaSy_ValidKey_WithSpaces   \n')
    def test_get_gemini_key_strips_whitespace(self, mock_file, mock_exists):
        """Test that key is stripped of whitespace."""
        key = get_gemini_key("gemini_key.txt")
        self.assertEqual(key, "AIzaSy_ValidKey_WithSpaces")


class TestGeminiAvailability(unittest.TestCase):
    """Test Gemini SDK availability detection."""

    def test_gemini_constants_exist_in_mission_builder(self):
        """Test that GEMINI constants are defined in MissionBuilder module."""
        # Import only the constants, not the class
        try:
            from utilities import MissionBuilder
            self.assertTrue(hasattr(MissionBuilder, 'GEMINI_AVAILABLE'))
            self.assertTrue(hasattr(MissionBuilder, 'GEMINI_VERSION'))
            self.assertIn(MissionBuilder.GEMINI_VERSION, [0, 1, 2])
        except ImportError:
            # If module can't be imported, skip this test
            self.skipTest("MissionBuilder module has import dependencies")

    def test_gemini_constants_exist_in_game_companion(self):
        """Test that GEMINI constants are defined in GameCompanion module."""
        try:
            from utilities import GameCompanion
            self.assertTrue(hasattr(GameCompanion, 'GEMINI_AVAILABLE'))
            self.assertTrue(hasattr(GameCompanion, 'GEMINI_VERSION'))
            self.assertIn(GameCompanion.GEMINI_VERSION, [0, 1, 2])
        except ImportError:
            self.skipTest("GameCompanion module has import dependencies")


class TestGeminiKeyValidation(unittest.TestCase):
    """Test API key validation logic."""

    def test_valid_key_format(self):
        """Test that valid API key formats are recognized."""
        # Google API keys typically start with 'AIzaSy'
        with patch('utilities.LegionUtils.os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data='AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ123456')):
                key = get_gemini_key()
                self.assertIsNotNone(key)
                self.assertTrue(key.startswith('AIzaSy'))

    def test_key_with_newlines(self):
        """Test that keys with trailing newlines are handled."""
        with patch('utilities.LegionUtils.os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data='my-api-key\n\n')):
                key = get_gemini_key()
                self.assertEqual(key, 'my-api-key')


if __name__ == '__main__':
    unittest.main()
