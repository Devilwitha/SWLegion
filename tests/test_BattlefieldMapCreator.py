import unittest
from unittest.mock import MagicMock, patch, mock_open, call
import os
import sys
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.BattlefieldMapCreator import BattlefieldMapCreator

class TestBattlefieldMapCreator(unittest.TestCase):
    @patch('utilities.BattlefieldMapCreator.tk')
    @patch('utilities.BattlefieldMapCreator.colorchooser')
    def setUp(self, mock_color, mock_tk):
        """Setup mock environment."""
        self.mock_root = MagicMock()
        # Mocking canvas
        self.mock_canvas = MagicMock()
        mock_tk.Canvas.return_value = self.mock_canvas
        
        self.creator = BattlefieldMapCreator(self.mock_root)
        
    def test_init(self):
        """Test initialization logic."""
        self.assertEqual(self.creator.mode, "select")
        self.assertEqual(self.creator.canvas_width, 720) # 6 * 120

    def test_set_mode(self):
        """Test changing modes."""
        self.creator.set_mode("rect")
        self.assertEqual(self.creator.mode, "rect")
        # Ensure label was updated
        self.creator.status_lbl.config.assert_called_with(text="Modus: Rect")

    @patch('utilities.BattlefieldMapCreator.filedialog.asksaveasfilename')
    @patch('utilities.BattlefieldMapCreator.get_writable_path', return_value='dummy')
    @patch('builtins.open', new_callable=mock_open)
    @patch('utilities.BattlefieldMapCreator.json.dump')
    def test_save_map(self, mock_json_dump, mock_file, mock_path, mock_ask):
        """Test saving logic."""
        mock_ask.return_value = "dummy.json"
        
        # Mock canvas items
        self.creator.canvas.find_all.return_value = [1]
        self.creator.canvas.gettags.return_value = ["shape"]
        self.creator.canvas.type.return_value = "rectangle"
        self.creator.canvas.coords.return_value = [0,0,10,10]
        self.creator.canvas.itemcget.side_effect = lambda i, opt: "red" if opt == "fill" else ""
        
        # Mock messagebox
        with patch('utilities.BattlefieldMapCreator.messagebox') as mock_msg:
             self.creator.save_map()
             
             # Check if file was opened
             mock_file.assert_called_with("dummy.json", "w")
             # Check if json.dump was called
             mock_json_dump.assert_called()
             # Verify data structure passed to dump
             args, _ = mock_json_dump.call_args
             data = args[0]
             self.assertEqual(len(data), 1)
             self.assertEqual(data[0]['type'], 'rectangle')
             self.assertEqual(data[0]['color'], 'red')

if __name__ == '__main__':
    unittest.main()
