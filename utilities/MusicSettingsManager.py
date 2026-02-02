import json
import os
import sys
from datetime import datetime

class MusicSettingsManager:
    """Verwaltet die Musikplayer-Einstellungen"""
    
    def __init__(self):
        # Bestimme Speicherpfad
        if getattr(sys, 'frozen', False):
            # EXE Modus
            exe_dir = os.path.dirname(sys.executable)
            self.settings_file = os.path.join(exe_dir, "music_player_settings.json")
        else:
            # Script Modus
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.settings_file = os.path.join(project_dir, "music_player_settings.json")
    
    def load_settings(self):
        """Lädt die gespeicherten Einstellungen"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden der Einstellungen: {e}")
        
        # Default-Einstellungen
        return {
            'volume': 70,
            'current_playlist': None,
            'current_song': None,
            'current_song_index': 0,
            'shuffle': False,
            'repeat': False,
            'last_updated': str(datetime.now())
        }
    
    def save_settings(self, settings):
        """Speichert die Einstellungen"""
        try:
            settings['last_updated'] = str(datetime.now())
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der Einstellungen: {e}")
    
    def update_setting(self, key, value):
        """Aktualisiert eine einzelne Einstellung"""
        settings = self.load_settings()
        settings[key] = value
        self.save_settings(settings)
    
    def get_setting(self, key, default=None):
        """Holt eine einzelne Einstellung"""
        settings = self.load_settings()
        return settings.get(key, default)