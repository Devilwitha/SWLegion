import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import sys
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.CustomUnitCreator import CustomUnitCreator

class TestCustomUnitCreator(unittest.TestCase):
    @patch('utilities.CustomUnitCreator.tk')
    @patch('utilities.CustomUnitCreator.get_data_path', return_value='dummy/path.json')
    @patch('utilities.CustomUnitCreator.os.path.exists')
    def setUp(self, mock_exists, mock_path, mock_tk):
        """Setup mock environment."""
        mock_exists.return_value = False # Start with no file
        self.mock_root = MagicMock()
        
        # Init creator
        self.creator = CustomUnitCreator(self.mock_root)
        
    @patch('builtins.open', new_callable=mock_open, read_data='[{"unit_data": {"name": "Test Unit"}}]')
    @patch('utilities.CustomUnitCreator.os.path.exists', return_value=True)
    def test_load_data(self, mock_exists, mock_file):
        """Test loading existing data."""
        data = self.creator.load_data()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['unit_data']['name'], "Test Unit")

    @patch('utilities.CustomUnitCreator.get_data_path', return_value='dummy/path.json') 
    @patch('builtins.open', new_callable=mock_open)
    def test_save_data(self, mock_file, mock_path):
        """Test saving data logic."""
        self.creator.units_data = [{"test": "data"}]
        # Mock messagebox to avoid popup
        with patch('utilities.CustomUnitCreator.messagebox'):
             self.creator.save_data()
        
        # Check if write was called
        mock_file.assert_called_with('dummy/path.json', 'w', encoding='utf-8')
        handle = mock_file()
        # Verify JSON dumping happened (rough check)
        handle.write.assert_called()

if __name__ == '__main__':
    unittest.main()
