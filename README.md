# Star Wars Legion: All-in-One Tool Suite

![Build Status](https://github.com/Devilwitha/SWLegion/actions/workflows/build-release-installer.yml/badge.svg)
![Latest Release](https://img.shields.io/github/v/release/Devilwitha/SWLegion)
![Downloads](https://img.shields.io/github/downloads/Devilwitha/SWLegion/total)

Dieses Projekt bietet eine Sammlung von digitalen Werkzeugen für das Tabletop-Spiel **Star Wars: Legion**. Es unterstützt Spieler beim Erstellen von Armeen, Generieren von Missionen und dient als digitaler Begleiter während des Spiels (inklusive AI-Gegner-Modus).

## 📋 Projektinformationen

**Code by:** BolliSoft (Nico Bollhalder)  
**Programm Version:** 1.1v  
**Regelwerk:** 2.5v  
**Github:** https://github.com/Devilwitha/SWLegion
**Neue Features:** Automatische CI/CD, Windows Installer, AI-Integration, Visual Marker System

## 🔽 Download & Installation

### Automatische Builds
Jeder GitHub Commit erstellt automatisch neue Releases mit beiden Installationsoptionen.

### Windows Installer (Empfohlen)
1. Lade die neueste Version von den [Releases](https://github.com/Devilwitha/SWLegion/releases) herunter
2. Führe `SWLegion_Installer.exe` aus und folge dem Setup-Assistenten
3. Starte das Programm über das Startmenü oder die Desktop-Verknüpfung
4. **Neu:** Automatische AppData-Verwaltung für Benutzerdaten

### Portable Version
1. Lade `SWLegion_Portable.zip` von den [Releases](https://github.com/Devilwitha/SWLegion/releases) herunter
2. Entpacke das ZIP-Archiv an einen beliebigen Ort
3. Führe `Start_SWLegion.bat` aus
4. **Dual-Mode:** Funktioniert identisch zur installierten Version

## 🚀 Schnellstart (Development)

### Voraussetzungen
*   Python 3.8+ muss installiert sein
*   Die folgenden Python-Pakete:
    ```bash
    pip install pillow requests
    ```
*   `tkinter` (standardmäßig in Python enthalten)

### Installation & Start
1.  Klone das Repository oder lade alle Dateien herunter
2.  Navigiere zum Projektordner
3.  Starte das Hauptmenü:
```bash
python MainMenu.py
```

## 📖 Empfohlene Nutzungsreihenfolge

### 1. 🏭 Custom Factory (Optional)
Erstelle eigene Inhalte für erweiterte Spielerfahrungen
*   Eigene Einheiten mit individuellen Statistiken
*   Benutzerdefinierte Kommando- und Schlachtkarten
*   Neue Waffen und Spezialfähigkeiten

### 2. 🏗️ Armee Builder
Baue deine Streitkräfte
*   Wähle Fraktion und Einheiten
*   Respektiere Punkt- und Rangbeschränkungen
*   Speichere deine Armee für das Spiel

### 3. 🗺️ Mission Generator
Erstelle spannende Szenarien
*   Nutze AI-gestützte Missionsgenerierung
*   Wähle Gelände und Aufstellungsarten
*   Exportiere Missionen für den Game Companion

### 4. 🎮 Game Companion
Spiele mit digitalem Support
*   Lade Mission und Armeen
*   Nutze Kampfsimulator und AI-Gegner
*   Verfolge Spielzustand und Rundenabläufe

---

## 🛠️ Die Module im Detail

### 1. Custom Factory (`CustomFactoryMenu.py`)
**Zweck:** Erweitere das Spiel mit eigenen Inhalten
*   **Custom Unit Creator:** Erstelle einzigartige Einheiten mit individuellen Werten
*   **Command Card Creator:** Designe eigene Kommandokarten
*   **Battle Card Creator:** Erstelle Missions- und Aufstellungskarten
*   **Upgrade Creator:** Entwickle neue Ausrüstung und Upgrades
*   **Integration:** Alle erstellten Inhalte stehen automatisch in anderen Modulen zur Verfügung

### 2. Armee Builder (`ArmeeBuilder.py`)
**Zweck:** Professionelles Armee-Management
### 2. Armee Builder (`ArmeeBuilder.py`)
**Zweck:** Professionelles Armee-Management
*   **Fraktionsauswahl:** Alle verfügbaren Fraktionen (Imperium, Rebellen, Republik, Separatisten, Schattenkollektiv)
*   **Einheitenverwaltung:** Zugriff auf offizielle und custom Einheiten
*   **Upgrade-System:** Ausrüstung und Verbesserungen zuweisen
*   **Automatische Validierung:** Punkt- und Rangbeschränkungen werden automatisch überprüft
*   **Kommandokarten:** Wähle 7 Karten für dein Deck
*   **Export/Import:** Speichere Armeen als .json für Game Companion

### 3. Mission Generator (`MissionBuilder.py`)
**Zweck:** Erstelle abwechslungsreiche Szenarien
*   **AI-gestützte Generierung:** Nutze Gemini AI für detaillierte Missionserzählungen
*   **Visualisierung:** Interaktive Schlachtfeldkarten mit Aufstellungszonen
*   **Anpassbarkeit:** Wähle Fraktionen, Gelände und Missionsziele
*   **Standard-Missionen:** Vorgefertigte Szenarien verfügbar
*   **Custom Battle Cards:** Integration eigener Missions- und Aufstellungskarten
*   **Export:** Speichere Missionen für Game Companion

### 4. Spiel-Begleiter & AI Simulator (`GameCompanion.py`)
**Zweck:** Digitaler Spielassistent mit KI-Unterstützung
*   **Rundenmanagement:** Automatische Phasenverfolgung (Kommando, Aktivierung, Ende)
*   **Order Pool System:** Digitale Befehlsmarker mit Zufallsziehung
*   **Visual Marker System:** 🎯 Aim, 💨 Dodge, 📉 Suppression, ⏸️ Panic Marker
*   **Kampf-Simulator:**
    *   Automatische Würfelberechnung (Angriff & Verteidigung)
    *   Pierce, Cover und Surge-Verarbeitung
    *   Direkter Schaden auf Zieleinheiten
*   **AI-Gegner:**
    *   Intelligente Entscheidungsfindung
    *   Automatische Zielpriorisierung
    *   Taktische Empfehlungen
*   **Zustandsverfolgung:** HP, Marker (Aim, Dodge, Suppression), Aktivierungen

## 📊 Erweiterte Funktionen

### Custom Content Integration
*   Alle selbst erstellten Inhalte werden automatisch in die Hauptdatenbank integriert
*   Custom Units erscheinen im Armee Builder
*   Custom Cards stehen im Mission Generator zur Verfügung
*   Vollständige Kompatibilität zwischen allen Modulen

### AI-Features
*   **Mission Generation:** GPT-basierte Szenario-Erstellung mit narrativen Hintergründen
*   **Tactical AI:** Intelligente Gegner-Steuerung im Game Companion
*   **Adaptive Difficulty:** AI passt sich an Spielsituationen an

### Datenmanagement
*   **Zentrale Datenbank:** `LegionData.py` verwaltet alle Einheiten, Waffen und Regeln
*   **Modulare Struktur:** `LegionRules.py` für Regelwerk-Referenzen
*   **Flexible Speicherung:** JSON-Format für einfache Bearbeitung und Backup

## � Entwicklung & CI/CD

### Automatische Builds
Jeder Push zum Repository löst automatisch aus:
1. **GitHub Actions Workflow** (.github/workflows/build-release-installer.yml)
2. **PyInstaller Kompilierung** (Windows Executable)
3. **Inno Setup Installer** (Professioneller Windows Installer)
4. **Release Creation** (Beide Download-Optionen)

### Build-System
```bash
# Lokaler Build (Windows)
cd build/Win
python -m PyInstaller --clean --noconfirm SWLegion.spec

# Installer erstellen
"C:\Program Files (x86)\Inno Setup 6\iscc.exe" SWLegion_Setup.iss
```

### Dual-Mode Kompatibilität
- **Script-Modus:** Direkter Python-Aufruf für Entwicklung
- **Executable-Modus:** Kompilierte Version für End-User
- **Intelligente Imports:** Automatische Erkennung des Ausführungsmodus
- **Permission-Safe:** AppData-Nutzung für installierte Anwendungen

## �🔧 Technische Details

### Architektur
```
MainMenu.py              # Hauptmenü und Launcher
├── utilities/           # Modulverzeichnis
│   ├── CustomFactoryMenu.py # Content Creation Hub
│   ├── ArmeeBuilder.py      # Army Management
│   ├── MissionBuilder.py    # Scenario Generation  
│   ├── GameCompanion.py     # Game Simulation
│   ├── BattlefieldMapCreator.py # Map Creator
│   ├── CardPrinter.py       # Card Export
│   ├── Custom*Creator.py    # Content Creators
│   ├── LegionData.py        # Core Database
│   ├── LegionRules.py       # Rules Reference
│   └── LegionUtils.py       # Utility Functions
├── .github/workflows/   # CI/CD Pipeline
├── build/Win/          # Build Configuration
└── db/                 # Database Files
```

### Dateistruktur
```
# Portable/Script-Modus:
/Armeen/                 # Gespeicherte Armeelisten
/Missions/              # Generierte Missionen
/maps/                  # Custom Schlachtfeldkarten
/custom_*.json          # Benutzerdefinierte Inhalte
/bilder/                # Programm-Assets
catalog.json            # Zentrale Einheitendatenbank

# Installierte Version:
%APPDATA%/Star Wars Legion Tool Suite/
├── Armeen/             # Benutzer-Armeen
├── Missions/           # Benutzer-Missionen 
├── maps/               # Benutzer-Karten
└── logs/               # Anwendungs-Logs
```

## 🎯 Tipps für optimale Nutzung

### Für Anfänger
1. Starte mit dem **Mission Generator** für dein erstes Spiel
2. Nutze vorgefertigte Armeen im **Game Companion**
3. Experimentiere mit dem **AI-Modus** für Solo-Spiele

### Für Fortgeschrittene
1. Erstelle eigene Inhalte in der **Custom Factory**
2. Baue thematische Armeen im **Armee Builder**
3. Entwickle komplexe Szenarien mit **AI-generierter Narrative**

### Für Turniere
1. Nutze den **Armee Builder** für regelkonforme Listen
2. **Game Companion** für schnelle Kampfberechnungen
3. **Mission Generator** für ausgewogene Szenarien

## 🐛 Problembehandlung

### Häufige Probleme
*   **AI-Features funktionieren nicht:** Überprüfe `gemini_key.txt` und Internet-Verbindung
*   **Bilder werden nicht geladen:** Stelle sicher, dass PIL/Pillow installiert ist
*   **Module starten nicht:** Überprüfe Python-Installation und Dateipfade
*   **Permission Denied Fehler:** Installierte Version nutzt automatisch AppData-Verzeichnis
*   **Import-Fehler:** Stelle sicher, dass alle utilities Module verfügbar sind
*   **Custom Creator startet nicht:** Überprüfe Dual-Mode Import-Kompatibilität

### Debug-Informationen
*   **Logs:** Automatisches Logging in `legion_app.log` (Script-Modus) oder AppData (Installiert)
*   **Execution Mode:** Automatische Erkennung von Script vs. Executable
*   **Path Resolution:** Intelligente Pfad-Auflösung für verschiedene Ausführungsmodi

### Support
Bei Problemen oder Fragen:
*   Erstelle ein Issue auf GitHub
*   Überprüfe die Logs in der Konsole
*   Stelle sicher, dass alle Abhängigkeiten installiert sind

---

## 🏆 Credits & Lizenz

**Entwickelt von:** BolliSoft (Nico Bollhalder)  
**Regelwerk:** Star Wars Legion 2.5v  
**Framework:** Python 3.8+ mit tkinter  

Dieses Projekt ist ein inoffizieller Fan-Content für Star Wars: Legion.
Star Wars und alle verwandten Marken sind Eigentum von Lucasfilm Ltd.

Star Wars, Star Wars: Legion and all related properties and text are owned by Fantasy Flight Games, Lucasfilm Ltd., and/or Disney. This a hobby and fun community app and resource and should strictly not be used for any commercial purchase.

---

*Möge die Macht mit dir sein! 🌟*
