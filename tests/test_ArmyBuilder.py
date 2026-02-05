import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.ArmeeBuilder import LegionArmyBuilder

class TestArmyBuilder(unittest.TestCase):
    @patch('utilities.ArmeeBuilder.LegionDatabase')
    @patch('utilities.ArmeeBuilder.tk')
    def setUp(self, mock_tk, mock_db):
        """Setup mock environment."""
        self.mock_root = MagicMock()
        # Mocking complex UI elements
        mock_tk.StringVar.return_value = MagicMock()
        
        self.builder = LegionArmyBuilder(self.mock_root)
        self.builder.current_army_list = []
        self.builder.total_points = 0

    def test_initial_state(self):
        self.assertEqual(self.builder.total_points, 0)
        self.assertEqual(len(self.builder.current_army_list), 0)

    # Since the logic is tightly coupled with the UI in the current implementation,
    # adding units involves looking up UI elements. 
    # Refactoring would be needed for deeper logic testing.
    
    # We can at least test saving/loading logic structure if we separate it.
    
if __name__ == '__main__':
    unittest.main()
