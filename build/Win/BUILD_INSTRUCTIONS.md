# Star Wars Legion - Windows Build Instructions

## 🔧 Entwickler-Anleitung für Windows-Kompilierung

### Voraussetzungen

1. **Python 3.8+** installiert
2. **Git** (optional, für Versionskontrolle)
3. **Windows 10/11** Entwicklungsumgebung

### 📦 Automatische Installation

```batch
# 1. Dependencies installieren
install_deps.bat

# 2. Anwendung kompilieren
build.bat
```

### 🛠️ Manuelle Installation

```batch
# Python Dependencies
pip install pyinstaller pillow requests

# Build ausführen
pyinstaller --clean --noconfirm SWLegion.spec
```

### 📁 Projektstruktur

```
SWLegion/
├── MainMenu.py              # Haupteinstiegspunkt
├── utilities/
│   ├── GameCompanion.py     # Spielbegleiter
│   ├── ArmeeBuilder.py      # Armeeneditor
│   ├── MissionBuilder.py    # Missionsgenerator
│   └── Custom*.py           # Factory Module
├── db/
│   └── catalog.json         # Spieledatenbank
├── build/Win/              # Build-Dateien
│   ├── SWLegion.spec       # PyInstaller Spezifikation
│   ├── build.bat           # Build-Script
│   ├── install_deps.bat    # Dependency-Installation
│   └── requirements.txt    # Python-Dependencies
└── dist/SWLegion/          # Kompilierte Anwendung
```

### ⚙️ Build-Konfiguration

**SWLegion.spec Haupteinstellungen:**
- `console=False`: GUI-Modus (keine Konsole)
- `upx=True`: Komprimierung aktiviert
- `icon='sw_legion_logo.ico'`: Anwendungs-Icon
- Alle `utilities/`, `db/`, `Armeen/` Ordner werden mitgepackt

### 🚀 Build-Prozess

1. **Vorbereitung:**
   ```
   cd build/Win
   install_deps.bat
   ```

2. **Kompilierung:**
   ```
   build.bat
   ```

3. **Ausgabe:**
   - Executable: `dist/SWLegion/SWLegion.exe`
   - Komplette Distribution: `dist/SWLegion/` Ordner

### 🐛 Debugging

**Für Fehlerdiagnose:**
1. In `SWLegion.spec`: `console=True` setzen
2. Build erneut ausführen
3. Konsole zeigt Fehlerdetails

**Häufige Probleme:**
- **Missing Module:** Dependency in `hiddenimports` hinzufügen
- **File not found:** Pfad in `datas` Sektion überprüfen
- **Import Error:** Module in `requirements.txt` ergänzen

### 📋 Build-Checklist

- [ ] Python 3.8+ installiert
- [ ] PyInstaller installiert
- [ ] Alle Dependencies verfügbar
- [ ] Spec-Datei aktualisiert
- [ ] Icon-Datei vorhanden
- [ ] Test auf sauberem System
- [ ] README_DISTRIBUTION.md aktualisiert

### 🚢 Distribution

**Für Endnutzer-Distribution:**
1. Kompletten `dist/SWLegion/` Ordner zippen
2. `README_DISTRIBUTION.md` beilegen
3. Version dokumentieren
4. Auf verschiedenen Windows-Systemen testen

### 🔄 Updates

**Bei Code-Änderungen:**
1. Neue Dependencies in `requirements.txt` ergänzen
2. Neue Dateien in `SWLegion.spec` `datas` hinzufügen
3. Version in `MainMenu.py` aktualisieren
4. Build erneut ausführen

---

**Hinweis:** Diese Build-Konfiguration erstellt eine portable Windows-Anwendung ohne Installer-Anforderungen.