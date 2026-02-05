import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.LegionData import LegionDatabase

class TestLegionData(unittest.TestCase):
    @patch('utilities.LegionData.LegionDatabase.load_catalog')
    @patch('utilities.LegionData.LegionDatabase.load_legacy') 
    @patch('utilities.LegionData.LegionDatabase.load_custom_units')
    @patch('utilities.LegionData.LegionDatabase.load_custom_command_cards')
    @patch('utilities.LegionData.LegionDatabase.load_custom_upgrades')
    @patch('utilities.LegionData.LegionDatabase.load_custom_battle_cards')
    def test_init_structure_mocked(self, mock_load_battle, mock_load_upgrades, mock_load_command, mock_load_units, mock_load_legacy, mock_load_catalog):
        """Test that LegionDatabase initializes structure without calling load methods."""
        db = LegionDatabase()
        
        self.assertIsInstance(db.units, dict)
        # Should be empty because we mocked all load calls
        self.assertEqual(db.upgrades, [])
        self.assertEqual(db.command_cards, [])
        self.assertEqual(db.battle_cards, [])
        
        # Verify load methods were called
        mock_load_catalog.assert_called_once()
        mock_load_legacy.assert_called_once()
        mock_load_units.assert_called_once()
        
    def test_translate(self):
        """Test the translate method."""
        # Partially mock init to avoid file IO but keep basic structure
        with patch('utilities.LegionData.LegionDatabase.load_catalog'), \
             patch('utilities.LegionData.LegionDatabase.load_legacy'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_units'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_command_cards'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_upgrades'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_battle_cards'):
            
            db = LegionDatabase()
            
            # Known translation
            self.assertEqual(db.translate("factions", "imperials"), "Galaktisches Imperium")
            # Unknown translation
            self.assertEqual(db.translate("factions", "unknown"), "Unknown")
            # Default value
            self.assertEqual(db.translate("factions", "unknown", default="Def"), "Def")

    def test_faction_translations(self):
        """Test all faction translations."""
        with patch('utilities.LegionData.LegionDatabase.load_catalog'), \
             patch('utilities.LegionData.LegionDatabase.load_legacy'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_units'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_command_cards'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_upgrades'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_battle_cards'):
            
            db = LegionDatabase()
            
            # Test known factions
            self.assertEqual(db.translate("factions", "rebels"), "Rebellenallianz")
            self.assertEqual(db.translate("factions", "republic"), "Galaktische Republik")
            self.assertEqual(db.translate("factions", "separatists"), "Separatistenallianz")

    def test_rank_translations(self):
        """Test rank translations."""
        with patch('utilities.LegionData.LegionDatabase.load_catalog'), \
             patch('utilities.LegionData.LegionDatabase.load_legacy'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_units'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_command_cards'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_upgrades'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_battle_cards'):
            
            db = LegionDatabase()
            
            # Test ranks - these use English names in the translation dict
            self.assertEqual(db.translate("ranks", "commander"), "Commander")
            self.assertEqual(db.translate("ranks", "corps"), "Corps")
            self.assertEqual(db.translate("ranks", "operative"), "Operative")

    def test_units_dict_structure(self):
        """Test units dictionary structure."""
        with patch('utilities.LegionData.LegionDatabase.load_catalog'), \
             patch('utilities.LegionData.LegionDatabase.load_legacy'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_units'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_command_cards'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_upgrades'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_battle_cards'):
            
            db = LegionDatabase()
            
            # Add a test unit
            db.units = {
                "test_unit": {"name": "Test Trooper", "points": 50}
            }
            
            # Test direct access
            self.assertIn("test_unit", db.units)
            self.assertEqual(db.units["test_unit"]["points"], 50)
            
            # Test non-existent unit
            self.assertNotIn("non_existent", db.units)


if __name__ == '__main__':
    unittest.main()

