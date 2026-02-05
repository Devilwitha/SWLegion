import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import sys
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.MusicSettingsManager import MusicSettingsManager

class TestMusicSettingsManager(unittest.TestCase):
    
    @patch('utilities.MusicSettingsManager.os.path.exists', return_value=False)
    @patch('utilities.MusicSettingsManager.sys')
    def test_load_defaults(self, mock_sys, mock_exists):
        """Test loading defaults when file misses."""
        # Use script mode path
        mock_sys.frozen = False
        manager = MusicSettingsManager()
        settings = manager.load_settings()
        
        self.assertEqual(settings['volume'], 70)
        self.assertEqual(settings['shuffle'], False)

    @patch('utilities.MusicSettingsManager.os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='{"volume": 50, "shuffle": true}')
    @patch('utilities.MusicSettingsManager.sys')
    def test_load_existing(self, mock_sys, mock_file, mock_exists):
        """Test loading from file."""
        mock_sys.frozen = False
        manager = MusicSettingsManager()
        settings = manager.load_settings()
        
        self.assertEqual(settings['volume'], 50)
        self.assertTrue(settings['shuffle'])
        
    @patch('utilities.MusicSettingsManager.sys')
    @patch('builtins.open', new_callable=mock_open)
    @patch('utilities.MusicSettingsManager.json.dump')    
    def test_save_settings(self, mock_dump, mock_file, mock_sys):
        """Test saving."""
        mock_sys.frozen = False
        manager = MusicSettingsManager()
        new_settings = {"volume": 80}
        
        manager.save_settings(new_settings)
        
        mock_file.assert_called()
        mock_dump.assert_called()
        args, _ = mock_dump.call_args
        self.assertEqual(args[0]['volume'], 80)
        self.assertIn('last_updated', args[0])

if __name__ == '__main__':
    unittest.main()
