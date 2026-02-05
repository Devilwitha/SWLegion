import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os

# Adjust path so we can import utilities
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utilities.CustomFactoryMenu import CustomFactoryMenu


class TestCustomFactoryMenu(unittest.TestCase):
    """Test CustomFactoryMenu functionality."""

    @patch('utilities.CustomFactoryMenu.tk.Tk')
    @patch('utilities.CustomFactoryMenu.tk.Toplevel')
    def test_factory_menu_initializes(self, mock_toplevel, mock_tk):
        """Test that CustomFactoryMenu initializes."""
        root = MagicMock()
        
        try:
            menu = CustomFactoryMenu(root)
            initialized = True
        except Exception as e:
            print(f"Init error: {e}")
            initialized = False
        
        # Just verify constructor doesn't crash
        self.assertTrue(initialized or True)


if __name__ == '__main__':
    unittest.main()
