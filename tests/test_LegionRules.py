import unittest
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.LegionRules import LegionRules

class TestLegionRules(unittest.TestCase):
    def test_phases_exist(self):
        """Test that main game phases are defined."""
        self.assertIn("setup", LegionRules.PHASES)
        self.assertIn("command", LegionRules.PHASES)
        self.assertIn("activation", LegionRules.PHASES)
        self.assertIn("end", LegionRules.PHASES)

    def test_actions_exist(self):
        """Test that standard actions are defined."""
        self.assertIn("move", LegionRules.ACTIONS)
        self.assertIn("attack", LegionRules.ACTIONS)
        self.assertIn("aim", LegionRules.ACTIONS)
        self.assertIn("dodge", LegionRules.ACTIONS)

    def test_conditions_exist(self):
        """Test that suppression/panic conditions are accessible."""
        # Note: Based on reading the code, CONDITIONS should be there
        self.assertTrue(hasattr(LegionRules, "CONDITIONS"))
        self.assertIn("suppressed", LegionRules.CONDITIONS)

if __name__ == '__main__':
    unittest.main()
