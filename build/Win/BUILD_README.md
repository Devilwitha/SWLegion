# Star Wars Legion - Windows Build System

## Übersicht
Dieses Verzeichnis enthält alle notwendigen Dateien zur Kompilierung der Star Wars Legion Anwendung für Windows.

## Dateien

### Build-Skripte
- `install_deps.bat` - Installiert alle erforderlichen Python-Pakete
- `build.bat` - Kompiliert die Anwendung zu einer Windows .exe-Datei
- `test.bat` - Testet die kompilierte Anwendung
- `SWLegion.spec` - PyInstaller-Konfigurationsdatei

### Konfiguration
- `requirements.txt` - Liste aller Python-Abhängigkeiten

## Verwendung

### 1. Abhängigkeiten installieren
```cmd
install_deps.bat
```

### 2. Anwendung kompilieren
```cmd
build.bat
```

### 3. Ergebnis testen
```cmd
test.bat
```

## Ausgabe
- Die kompilierte Anwendung befindet sich in: `dist/SWLegion/SWLegion.exe`
- Alle Abhängigkeiten sind im `dist/SWLegion/` Verzeichnis enthalten
- Das gesamte `dist/SWLegion/` Verzeichnis kann auf andere Windows-Computer kopiert werden

## Features der kompilierten Version v2.2 (Final)
- ✅ Vollständig eigenständige .exe-Datei mit SW Legion Icon
- ✅ Alle Python-Module eingebettet mit korrigierten Imports
- ✅ Direkte Modulausführung (kein subprocess mehr)
- ✅ Kein "Datei nicht gefunden" Fehler mehr für .py-Dateien
- ✅ PNG-Bilder werden korrekt aus _internal geladen
- ✅ Marker-System mit Emojis (🎯💨📉⏸️)
- ✅ Utilities-Module integriert und funktional
- ✅ Spieldaten und Konfigurationsdateien enthalten
- ✅ Custom Factory, Armee Builder und alle Module funktionsfähig

## System-Anforderungen
- Windows 10/11 (64-bit)
- Keine Python-Installation erforderlich
- Keine zusätzlichen Abhängigkeiten erforderlich

## Fehlerbehebung
Falls Probleme auftreten, überprüfen Sie:
1. Alle Quelldateien sind im Hauptverzeichnis vorhanden
2. Die SWLegion.spec Datei enthält alle benötigten Pfade
3. PyInstaller ist korrekt installiert

## Version
Build-System erstellt: Februar 2026
Letzte Aktualisierung: Marker-System vollständig implementiert