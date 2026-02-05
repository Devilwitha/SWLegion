import unittest
import os
import sys
import shutil

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.LegionUtils import get_data_path, get_writable_path

class TestLegionUtils(unittest.TestCase):
    def test_get_data_path_script_mode(self):
        """Test path resolution when running as a script."""
        # Mock sys.frozen = False
        if hasattr(sys, 'frozen'):
            delattr(sys, 'frozen')
            
        test_file = "README.md"
        result = get_data_path(test_file)
        # Should be absolute path ending in README.md
        self.assertTrue(os.path.isabs(result))
        self.assertTrue(result.endswith(test_file))

    def test_get_writable_path(self):
        """Test that writable path returns a valid directory."""
        folder_name = "TestFolder"
        result = get_writable_path(folder_name)
        
        self.assertTrue(os.path.exists(result))
        self.assertTrue(os.path.isdir(result))
        self.assertTrue(result.endswith(folder_name))
        
        # Cleanup
        try:
            os.rmdir(result)
        except:
            pass

if __name__ == '__main__':
    unittest.main()
