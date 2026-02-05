import unittest
from unittest.mock import patch, mock_open
import os
import sys
import shutil

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.LegionUtils import get_data_path, get_writable_path, get_gemini_key

class TestLegionUtils(unittest.TestCase):
    def test_get_data_path_script_mode(self):
        """Test path resolution when running as a script."""
        # Mock sys.frozen = False
        if hasattr(sys, 'frozen'):
            delattr(sys, 'frozen')
            
        test_file = "README.md"
        result = get_data_path(test_file)
        # Should be absolute path ending in README.md
        self.assertTrue(os.path.isabs(result))
        self.assertTrue(result.endswith(test_file))

    def test_get_writable_path(self):
        """Test that writable path returns a valid directory."""
        folder_name = "TestFolder"
        result = get_writable_path(folder_name)
        
        self.assertTrue(os.path.exists(result))
        self.assertTrue(os.path.isdir(result))
        self.assertTrue(result.endswith(folder_name))
        
        # Cleanup
        try:
            os.rmdir(result)
        except:
            pass


class TestGeminiKey(unittest.TestCase):
    """Test Gemini API key functions."""
    
    @patch('utilities.LegionUtils.os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='my-valid-api-key')
    def test_get_gemini_key_valid(self, mock_file, mock_exists):
        """Test valid key retrieval."""
        key = get_gemini_key()
        self.assertEqual(key, "my-valid-api-key")
    
    @patch('utilities.LegionUtils.os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='BITTE_HIER_API_KEY_EINFUEGEN')
    def test_get_gemini_key_placeholder_returns_none(self, mock_file, mock_exists):
        """Test that placeholder returns None."""
        key = get_gemini_key()
        self.assertIsNone(key)
    
    @patch('utilities.LegionUtils.os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='')
    def test_get_gemini_key_empty_returns_none(self, mock_file, mock_exists):
        """Test that empty file returns None."""
        key = get_gemini_key()
        self.assertIsNone(key)
    
    @patch('utilities.LegionUtils.os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='  AIzaSy_key_with_spaces  \n')
    def test_get_gemini_key_strips_whitespace(self, mock_file, mock_exists):
        """Test whitespace stripping."""
        key = get_gemini_key()
        self.assertEqual(key, "AIzaSy_key_with_spaces")


if __name__ == '__main__':
    unittest.main()
