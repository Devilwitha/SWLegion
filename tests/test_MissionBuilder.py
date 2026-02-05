import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.MissionBuilder import LegionMissionGenerator
from utilities.LegionData import LegionDatabase

class TestMissionBuilder(unittest.TestCase):
    @patch('utilities.MissionBuilder.LegionDatabase')
    @patch('utilities.MissionBuilder.tk')
    @patch('utilities.MissionBuilder.ttk')
    def setUp(self, mock_ttk, mock_tk, mock_db):
        """Setup with mocked UI and DB"""
        self.mock_root = MagicMock()
        mock_tk.StringVar.return_value = MagicMock()
        mock_tk.IntVar.return_value = MagicMock()
        
        # Mock database categories
        instance = mock_db.return_value
        instance.battle_cards = []
        instance.units = {"Empire": [], "Rebels": []}
        
        self.builder = LegionMissionGenerator(self.mock_root)
        
    def test_default_lists(self):
        """Test that default mission types are populated."""
        self.assertTrue(len(self.builder.default_deployments) > 0)
        self.assertIn("Battle Lines", self.builder.default_deployments)
        self.assertIn("Abfangen (Intercept)", self.builder.default_missions)

    @patch('utilities.MissionBuilder.messagebox')
    @patch('utilities.MissionBuilder.filedialog.asksaveasfilename')
    @patch('utilities.MissionBuilder.get_writable_path', return_value='dummy')
    @patch('builtins.open', new_callable=mock_open)
    @patch('utilities.MissionBuilder.json.dump')    
    @patch('utilities.MissionBuilder.os.path.exists', return_value=True) # Map logic
    def test_save_mission_logic(self, mock_exists, mock_json, mock_file, mock_path, mock_ask, mock_msg):
        """Test gathering data and saving mission."""
        
        # Setup inputs
        self.builder.combo_deploy = MagicMock()
        self.builder.combo_deploy.get.return_value = "Battle Lines"
        
        self.builder.combo_mission = MagicMock()
        self.builder.combo_mission.get.return_value = "Intercept"
        
        self.builder.combo_blue = MagicMock()
        self.builder.combo_blue.get.return_value = "Rebels"
        
        self.builder.combo_red = MagicMock()
        self.builder.combo_red.get.return_value = "Empire"
        
        self.builder.entry_punkte = MagicMock()
        self.builder.entry_punkte.get.return_value = "800"
        
        self.builder.entry_runden = MagicMock()
        self.builder.entry_runden.get.return_value = "6"
        
        self.builder.txt_output = MagicMock()
        self.builder.txt_output.get.return_value = "Scenario Text"
        self.builder.current_scenario_text = "Scenario Text"
        
        self.builder.var_gelaende = {} # Mock checkbox dict if needed

        # Execute save
        mock_ask.return_value = "mission.json"
        
        # Since 'generate_map_image' is called, it might try to save an image.
        # We should patch generate_map_image to avoid FS ops
        with patch.object(self.builder, 'generate_map_image', return_value='map.png'):
            self.builder.save_mission()
        
        # Verify JSON dump
        self.assertTrue(mock_json.called)
        
        # Find the call that contains mission data
        mission_data = None
        for call in mock_json.call_args_list:
            args, _ = call
            # Check for a specific key that should be in mission data
            if isinstance(args[0], dict) and "deployment" in args[0]:
                mission_data = args[0]
                break
        
        self.assertIsNotNone(mission_data, "Mission data was not saved via json.dump")
        
        self.assertEqual(mission_data.get("deployment"), "Battle Lines")
        self.assertEqual(mission_data.get("blue_faction"), "Rebels")
        self.assertEqual(mission_data.get("points"), "800")
        
        # Verify file open was called correctly for the mission file
        # mock_file might be called multiple times (mission json, music settings, etc.)
        # check if ANY call used "mission.json"
        
        mission_file_opened = False
        for call in mock_file.call_args_list:
            args, _ = call
            if args[0] == "mission.json":
                mission_file_opened = True
                break
        self.assertTrue(mission_file_opened)

if __name__ == '__main__':
    unittest.main()
