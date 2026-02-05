import unittest
from unittest.mock import MagicMock, patch
import os
import sys
from PIL import Image

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.MapRenderer import MapRenderer

class TestMapRenderer(unittest.TestCase):
    def test_draw_map_standard(self):
        """Test generating a standard map image."""
        img = MapRenderer.draw_map("Battle Lines")
        self.assertIsInstance(img, Image.Image)
        self.assertEqual(img.size, (800, 400))

    def test_draw_map_unknown(self):
        """Test generating a map with unknown mode returns a base image."""
        img = MapRenderer.draw_map("Unknown Mode")
        self.assertIsInstance(img, Image.Image)

    def test_draw_overlays(self):
        """Test adding overlays to an image."""
        base_img = Image.new("RGB", (800, 400), "white")
        img = MapRenderer.draw_overlays(base_img, "Intercept", "Empire", "Rebels")
        self.assertIsInstance(img, Image.Image)

    @patch('utilities.MapRenderer.ImageDraw.Draw')
    def test_draw_overlays_calls_draw(self, mock_draw):
        """Test that drawing methods are actually called."""
        base_img = Image.new("RGB", (800, 400), "white")
        MapRenderer.draw_overlays(base_img, "Abfangen")
        mock_draw.assert_called()

if __name__ == '__main__':
    unittest.main()
