import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import json

# Adjust path so we can import utilities
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utilities.CustomBattleCardCreator import CustomBattleCardCreator

class TestCustomBattleCardCreator(unittest.TestCase):

    @patch('utilities.CustomBattleCardCreator.tk.Tk')
    @patch('builtins.open', new_callable=mock_open)
    @patch('utilities.CustomBattleCardCreator.get_writable_path', return_value='dummy_path')
    @patch('utilities.CustomBattleCardCreator.get_data_path', return_value='dummy_db.json')
    @patch('utilities.CustomBattleCardCreator.json.load')
    @patch('utilities.CustomBattleCardCreator.os.path.exists')
    def setUp(self, mock_exists, mock_json_load, mock_get_data, mock_get_writable, mock_file, mock_tk):
        mock_exists.return_value = True
        mock_json_load.return_value = [{"id": "1", "name": "Existing Card"}]
        
        self.root = MagicMock()
        self.creator = CustomBattleCardCreator(self.root)

    def test_load_data(self):
        """Test loading data from JSON."""
        self.assertEqual(len(self.creator.cards_data), 1)
        self.assertEqual(self.creator.cards_data[0]["name"], "Existing Card")

    @patch('utilities.CustomBattleCardCreator.json.dump')
    @patch('builtins.open', new_callable=mock_open)
    @patch('utilities.CustomBattleCardCreator.messagebox')
    def test_save_data(self, mock_msg, mock_file, mock_json_dump):
        """Test saving data completely."""
        self.creator.cards_data = [{"id": "2", "name": "New Card"}]
        self.creator.save_data()
        
        mock_file.assert_called_with('dummy_db.json', 'w', encoding='utf-8')
        mock_json_dump.assert_called()
        args, _ = mock_json_dump.call_args
        self.assertEqual(args[0], [{"id": "2", "name": "New Card"}])
        mock_msg.showinfo.assert_called()

if __name__ == '__main__':
    unittest.main()
