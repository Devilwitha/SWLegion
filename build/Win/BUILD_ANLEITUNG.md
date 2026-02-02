# Star Wars Legion - Build Instructions

## Zusammenfassung der Änderungen

### 1. Enhanced Logging System
- **Datei**: `utilities/LegionUtils.py`
- **Funktion**: Umfassendes Logging mit DEBUG-Level
- **Features**: 
  - Alle Fehler werden in `legion_app.log` gespeichert
  - Console zeigt nur INFO+ Nachrichten
  - Unhandled Exceptions werden automatisch geloggt
  - Detaillierte Traceback-Informationen

### 2. Improved Error Handling
- **Datei**: `MainMenu.py`
- **Verbesserungen**:
  - Detaillierte Logging bei jedem Import-Versuch
  - Separate Exception-Behandlung für Import- und Runtime-Fehler
  - System-State Logging für bessere Debugging-Info
  - Benutzerfreundliche Fehlermeldungen mit Hinweis auf Log

### 3. Inno Setup Installer
- **Datei**: `build/Win/SWLegion_Setup.iss`
- **Features**:
  - Professioneller Windows Installer
  - Deutsche und englische Sprache
  - Desktop-Icon (optional)
  - Automatische Deinstallation alter Versionen
  - Start-Menü Einträge

## Build-Prozess

### Schritt 1: Executable erstellen
```bat
cd build\Win
build_enhanced.bat
```

### Schritt 2: Installer erstellen (optional)
```bat
cd build\Win
build_installer.bat
```

## Troubleshooting

### 1. Logging überprüfen
Nach dem Start der Anwendung wird automatisch `legion_app.log` erstellt.
Diese Datei enthält alle Debug-Informationen und Fehler.

### 2. Häufige Probleme

**Import-Fehler**: 
- Prüfen Sie das Log nach "Import error" Nachrichten
- Stellen Sie sicher, dass alle Module im `utilities/` Ordner sind

**PyInstaller Detection**:
- Das Log zeigt den Erkennungsstatus an
- Multiple Erkennungsmethoden implementiert

**Resource-Pfade**:
- Bilder werden aus `_internal/bilder/` geladen
- PNG-Dateien sind in der .spec-Datei definiert

### 3. Debug-Modus
Für maximale Debug-Informationen:
```python
# In der Anwendung wird automatisch DEBUG-Level logging aktiviert
# Keine manuelle Konfiguration nötig
```

## File Structure
```
SWLegion/
├── build/Win/
│   ├── SWLegion.spec          # PyInstaller Konfiguration
│   ├── build.bat              # Standard Build
│   ├── build_enhanced.bat     # Build mit Testing
│   ├── build_installer.bat    # Installer Build
│   └── SWLegion_Setup.iss     # Inno Setup Script
├── utilities/
│   ├── __init__.py            # Module exports
│   ├── LegionUtils.py         # Enhanced logging
│   └── [andere Module...]
├── MainMenu.py                # Enhanced error handling
└── legion_app.log             # Auto-generierte Log-Datei
```

## Requirements
- Python 3.11.9+
- PyInstaller 6.18.0+
- PIL/Pillow 10.4.0+
- Inno Setup (für Installer)

## Nächste Schritte
1. Testen Sie das neue Build-System mit `build_enhanced.bat`
2. Überprüfen Sie das Log auf eventuelle Fehler
3. Bei Problemen: Log-Datei analysieren für detaillierte Fehlerinformationen
4. Installer mit `build_installer.bat` erstellen