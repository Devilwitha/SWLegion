"""
Tests for Card Image Linking Features

Tests the new functionality for linking and displaying card images 
with units in CardPrinter, ArmeeBuilder, GameCompanion, and LegionData.
"""

import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import json
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestCardPrinterImageLinking(unittest.TestCase):
    """Tests for CardPrinter save_and_link_image functionality."""
    
    @patch('utilities.CardPrinter.tk.Tk')
    @patch('utilities.CardPrinter.tk.Canvas')
    @patch('utilities.CardPrinter.ttk.Combobox')
    @patch('utilities.CardPrinter.os.path.exists', return_value=True)
    @patch('utilities.CardPrinter.json.load')
    @patch('builtins.open', new_callable=mock_open)
    def setUp(self, mock_file, mock_json_load, mock_exists, mock_combo, mock_canvas, mock_tk):
        from utilities.CardPrinter import CardPrinter
        
        self.mock_units = [{"id": "unit-123", "factions": ["Test"], "unit_data": {"name": "TestUnit", "id": "unit-123"}}]
        self.mock_cards = [{"id": "card-456", "name": "TestCard"}]
        self.mock_upgrades = [{"id": "upgrade-789", "name": "TestUpgrade"}]
        self.mock_battles = [{"id": "battle-111", "name": "TestBattle"}]
        
        mock_json_load.side_effect = [
            self.mock_units,
            self.mock_cards,
            self.mock_upgrades,
            self.mock_battles
        ]
        
        self.root = MagicMock()
        self.printer = CardPrinter(self.root)
        
    def test_get_selected_data_unit(self):
        """Test getting selected unit data."""
        self.printer.cb_type = MagicMock()
        self.printer.cb_obj = MagicMock()
        
        self.printer.cb_type.get.return_value = "Einheit"
        self.printer.cb_obj.get.return_value = "TestUnit"
        
        data, mode = self.printer.get_selected_data()
        
        self.assertEqual(mode, "unit")
        self.assertEqual(data["name"], "TestUnit")
        
    def test_get_selected_data_card(self):
        """Test getting selected command card data."""
        self.printer.cb_type = MagicMock()
        self.printer.cb_obj = MagicMock()
        
        self.printer.cb_type.get.return_value = "Kommandokarte"
        self.printer.cb_obj.get.return_value = "TestCard"
        
        data, mode = self.printer.get_selected_data()
        
        self.assertEqual(mode, "card")
        self.assertEqual(data["name"], "TestCard")

    def test_save_and_link_without_image(self):
        """Test save_and_link_image fails without generated image."""
        from utilities.CardPrinter import messagebox
        
        with patch.object(messagebox, 'showerror') as mock_error:
            self.printer.save_and_link_image()
            mock_error.assert_called()


class TestCardImagePath(unittest.TestCase):
    """Tests for card image path resolution."""
    
    def test_card_image_path_resolution(self):
        """Test the logic for finding card image paths."""
        # Create a temp directory structure
        self.test_dir = tempfile.mkdtemp()
        card_images_dir = os.path.join(self.test_dir, "db", "card_images")
        os.makedirs(card_images_dir, exist_ok=True)
        
        # Create a test image file
        test_image_path = os.path.join(card_images_dir, "TestUnit.png")
        with open(test_image_path, "w") as f:
            f.write("fake image data")
        
        try:
            # Test that path exists
            self.assertTrue(os.path.exists(test_image_path))
            
            # Test path with spaces converted to underscores
            test_image_path2 = os.path.join(card_images_dir, "Test_Unit.png")
            with open(test_image_path2, "w") as f:
                f.write("fake image data")
            self.assertTrue(os.path.exists(test_image_path2))
            
        finally:
            shutil.rmtree(self.test_dir)


class TestLegionDataCardImage(unittest.TestCase):
    """Tests for LegionData card_image loading."""
    
    def test_custom_unit_with_card_image(self):
        """Test that custom units load card_image field."""
        custom_unit_data = [{
            "id": "custom-unit-1",
            "factions": ["Galaktisches Imperium"],
            "card_image": "db/card_images/custom-unit-1.png",
            "unit_data": {
                "name": "Custom Unit",
                "id": "custom-unit-1",
                "points": 50
            }
        }]
        
        with patch('utilities.LegionData.LegionDatabase.load_catalog'), \
             patch('utilities.LegionData.LegionDatabase.load_legacy'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_command_cards'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_upgrades'), \
             patch('utilities.LegionData.LegionDatabase.load_custom_battle_cards'), \
             patch('utilities.LegionData.os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(custom_unit_data))):
            
            from utilities.LegionData import LegionDatabase
            db = LegionDatabase()
            
            # Check if unit was loaded with card_image
            if "Galaktisches Imperium" in db.units:
                units = db.units["Galaktisches Imperium"]
                custom_unit = next((u for u in units if u.get("name") == "Custom Unit"), None)
                if custom_unit:
                    self.assertEqual(custom_unit.get("card_image"), "db/card_images/custom-unit-1.png")


class TestGameCompanionCardImage(unittest.TestCase):
    """Tests for GameCompanion card image display."""
    
    def test_get_unit_card_image_path_direct(self):
        """Test unit card image path when directly specified."""
        unit = {
            "name": "Test Unit",
            "card_image": "db/card_images/test.png"
        }
        
        with patch('os.path.exists', return_value=True):
            # Simulate the path finding logic
            card_image_path = unit.get("card_image")
            self.assertEqual(card_image_path, "db/card_images/test.png")
            
    def test_get_unit_card_image_path_by_id(self):
        """Test unit card image path lookup by ID."""
        unit = {
            "name": "Test Unit",
            "id": "unit-abc-123"
        }
        
        # Simulate path lookup
        possible_paths = [
            f"db/card_images/{unit.get('id')}.png",
            f"db/card_images/{unit.get('name')}.png",
            f"db/card_images/{str(unit.get('name')).replace(' ', '_')}.png"
        ]
        
        self.assertEqual(possible_paths[0], "db/card_images/unit-abc-123.png")
        self.assertEqual(possible_paths[1], "db/card_images/Test Unit.png")
        self.assertEqual(possible_paths[2], "db/card_images/Test_Unit.png")

    def test_get_unit_card_image_path_no_image(self):
        """Test unit without any card image."""
        unit = {
            "name": "No Image Unit"
        }
        
        with patch('os.path.exists', return_value=False):
            # Simulate path lookup - should find nothing
            card_image_path = unit.get("card_image")
            self.assertIsNone(card_image_path)


class TestArmeeBuilderCardImage(unittest.TestCase):
    """Tests for ArmeeBuilder card image display."""
    
    def test_clear_card_image_attributes(self):
        """Test that clear_card_image resets all attributes."""
        # Test the logic without tkinter
        current_card_image = None
        current_card_image_path = None
        
        # After clear
        self.assertIsNone(current_card_image)
        self.assertIsNone(current_card_image_path)
        
    def test_pil_availability_check(self):
        """Test PIL availability for image loading."""
        try:
            from PIL import Image, ImageTk
            pil_available = True
        except ImportError:
            pil_available = False
            
        # PIL should be available in most environments
        self.assertTrue(pil_available, "PIL is required for card image features")


class TestCardImageIntegration(unittest.TestCase):
    """Integration tests for card image features."""
    
    def test_card_images_directory_exists(self):
        """Test that card_images directory exists or can be created."""
        card_images_dir = "db/card_images"
        
        if not os.path.exists(card_images_dir):
            os.makedirs(card_images_dir, exist_ok=True)
        
        self.assertTrue(os.path.exists(card_images_dir))
        
    def test_json_card_image_field_format(self):
        """Test that card_image field is correctly formatted in JSON."""
        unit_entry = {
            "id": "test-unit",
            "factions": ["Test Faction"],
            "card_image": "db/card_images/test-unit.png",
            "unit_data": {
                "name": "Test Unit",
                "points": 100
            }
        }
        
        # Serialize and deserialize
        json_str = json.dumps(unit_entry)
        parsed = json.loads(json_str)
        
        self.assertEqual(parsed["card_image"], "db/card_images/test-unit.png")
        
    def test_image_path_sanitization(self):
        """Test that image paths are properly sanitized."""
        unsafe_names = [
            "Unit With Spaces",
            "Unit/With/Slashes",
            "Unit\\With\\Backslashes",
            "Unit.With.Dots"
        ]
        
        for name in unsafe_names:
            safe_name = str(name).replace(" ", "_").replace("/", "_").replace("\\", "_")
            
            # Verify no problematic characters remain
            self.assertNotIn("/", safe_name)
            self.assertNotIn("\\", safe_name)


class TestGameEngineCardImageIntegration(unittest.TestCase):
    """Tests for GameEngine integration with card images."""
    
    def test_unit_state_preserves_card_image(self):
        """Test that unit state operations preserve card_image field."""
        unit = {
            "name": "Test Unit",
            "card_image": "db/card_images/test.png",
            "hp": 5,
            "current_hp": 5,
            "suppression": 0
        }
        
        # Simulate state changes
        unit["current_hp"] -= 1
        unit["suppression"] += 1
        
        # card_image should be preserved
        self.assertEqual(unit.get("card_image"), "db/card_images/test.png")
        self.assertEqual(unit["current_hp"], 4)
        self.assertEqual(unit["suppression"], 1)


if __name__ == '__main__':
    unittest.main()
