import unittest
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.LegionRules import LegionRules

class TestLegionRulesExtended(unittest.TestCase):
    def test_phase_logic(self):
        """Test specific rule contents."""
        setup = LegionRules.PHASES["setup"]
        self.assertTrue(len(setup["steps"]) > 0)
        # Check if any step contains "Armeezusammenstellung"
        self.assertTrue(any("Armeezusammenstellung" in step for step in setup["steps"]))

    def test_action_descriptions(self):
        """Test that actions have descriptions."""
        move = LegionRules.ACTIONS["move"]
        self.assertTrue(len(move["description"]) > 5)

if __name__ == '__main__':
    unittest.main()
