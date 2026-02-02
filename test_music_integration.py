"""
Test script for the music integration in SW Legion
Tests the complete workflow from MissionBuilder music setup to auto-launch
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.MusicSettingsManager import MusicSettingsManager
from utilities.MusicPlayer import MusicPlayer

def test_music_settings():
    """Test the music settings manager"""
    print("Testing MusicSettingsManager...")
    
    # Create settings manager
    settings_manager = MusicSettingsManager()
    
    # Test saving and loading settings
    test_settings = {
        'volume': 85,
        'current_playlist': 'Test Playlist',
        'current_song_index': 2,
        'shuffle': True,
        'repeat': False
    }
    
    for key, value in test_settings.items():
        settings_manager.update_setting(key, value)
        print(f"Saved {key}: {value}")
    
    # Load settings and verify
    loaded_settings = settings_manager.load_settings()
    print(f"\nLoaded settings: {loaded_settings}")
    
    for key, expected_value in test_settings.items():
        actual_value = loaded_settings.get(key)
        if actual_value == expected_value:
            print(f"✓ {key}: {actual_value} (correct)")
        else:
            print(f"✗ {key}: expected {expected_value}, got {actual_value}")

def test_playlist_launch():
    """Test launching music player with playlist"""
    print("\n\nTesting playlist auto-launch...")
    
    # This would normally be called from MissionBuilder
    # For testing, we'll simulate it
    try:
        thread = MusicPlayer.launch_with_playlist("Battle Music")
        print("✓ Music player thread started successfully")
        print("Note: If playlist 'Battle Music' exists, it should auto-start playing")
        return thread
    except Exception as e:
        print(f"✗ Error launching music player: {e}")
        return None

if __name__ == "__main__":
    print("=== SW Legion Music Integration Test ===\n")
    
    # Test 1: Settings persistence
    test_music_settings()
    
    # Test 2: Playlist auto-launch
    thread = test_playlist_launch()
    
    print("\n=== Test Complete ===")
    print("If a music player window opened and started playing, the integration is working!")
    print("You can test the MissionBuilder music options by running it and creating a mission with music enabled.")