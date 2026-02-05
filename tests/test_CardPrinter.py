import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os

# Adjust path so we can import utilities
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utilities.CardPrinter import CardPrinter

class TestCardPrinter(unittest.TestCase):

    @patch('utilities.CardPrinter.tk.Tk')
    @patch('utilities.CardPrinter.tk.Canvas') # Canvas is used in setup_ui
    @patch('utilities.CardPrinter.ttk.Combobox')
    @patch('utilities.CardPrinter.os.path.exists', return_value=True)
    @patch('utilities.CardPrinter.json.load')
    @patch('builtins.open', new_callable=mock_open)
    def setUp(self, mock_file, mock_json_load, mock_exists, mock_combo, mock_canvas, mock_tk):
        
        # Test data
        self.mock_units = [{"unit_data": {"name": "Trooper"}}]
        self.mock_cards = [{"name": "Ambush"}]
        self.mock_upgrades = [{"name": "Scope"}]
        self.mock_battles = [{"name": "Intercept"}]
        
        # Configure json.load to return different things based on file name?
        # Since json.load is called multiple times in __init__, side_effect works best.
        mock_json_load.side_effect = [
            self.mock_units,     # units
            self.mock_cards,     # command
            self.mock_upgrades,  # upgrades
            self.mock_battles    # battle
        ]
        
        self.root = MagicMock()
        self.printer = CardPrinter(self.root)
        
        # Capture mocks
        self.mock_combo = mock_combo

    def test_initial_data_load(self):
        """Test that data is loaded into lists."""
        self.assertEqual(len(self.printer.units_data), 1)
        self.assertEqual(len(self.printer.cards_data), 1)
        
    def test_update_obj_list(self):
        """Test updating object list based on selection."""
        # By default in setup_ui, current(0) is set which is "Einheit"
        # And update_obj_list is called.
        
        # Setup mocks for interaction
        self.printer.cb_type = MagicMock()
        self.printer.cb_obj = MagicMock()
        
        # 1. Test "Einheit"
        self.printer.cb_type.get.return_value = "Einheit"
        self.printer.update_obj_list()
        
        # Verify setitem was called for 'values'
        # Since catching setitem on PropertyMock or MagicMock can be tricky,
        # we can verify that .current(0) was called, which implies values were found and set.
        self.printer.cb_obj.current.assert_called_with(0)
        
        # 2. Test "Ausrüstung"
        self.printer.cb_type.get.return_value = "Ausrüstung"
        self.printer.update_obj_list()
        self.printer.cb_obj.current.assert_called_with(0)

    @patch('utilities.CardPrinter.filedialog.askopenfilename')
    def test_upload_image(self, mock_ask):
        """Test image upload dialog."""
        mock_ask.return_value = "test.png"
        with patch('utilities.CardPrinter.Image.open') as mock_img_open:
            self.printer.upload_image()
            mock_img_open.assert_called_with("test.png")
            self.assertIsNotNone(self.printer.loaded_image)

if __name__ == '__main__':
    unittest.main()
