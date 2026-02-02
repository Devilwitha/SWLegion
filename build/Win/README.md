# Star Wars Legion - Windows Build System

## 🚀 Schnellstart

```batch
# 1. Dependencies installieren
install_deps.bat

# 2. Anwendung kompilieren  
build.bat

# 3. Testen
test.bat
```

## 📁 Dateien im Build-Ordner

| Datei | Beschreibung |
|-------|-------------|
| `SWLegion.spec` | PyInstaller Konfiguration |
| `build.bat` | Hauptbuild-Script |
| `install_deps.bat` | Dependency Installation |
| `clean.bat` | Build-Artifacts löschen |
| `test.bat` | Executable testen |
| `requirements.txt` | Python Dependencies |
| `BUILD_INSTRUCTIONS.md` | Detaillierte Anweisungen |
| `README_DISTRIBUTION.md` | Endnutzer-Dokumentation |

## ⚡ Build-Kommandos

```batch
# Vollständiger Clean Build
clean.bat && install_deps.bat && build.bat

# Nur neu kompilieren (nach Code-Änderungen)
build.bat

# Build testen
test.bat
```

## 📦 Ausgabe

Nach erfolgreichem Build finden Sie:
- **Executable:** `dist/SWLegion/SWLegion.exe`
- **Distribution:** Kompletter `dist/SWLegion/` Ordner

## 🔧 Anpassungen

**Für Custom Builds:**
1. `SWLegion.spec` bearbeiten
2. Dependencies in `requirements.txt` anpassen
3. `build.bat` ausführen

## 🐛 Troubleshooting

| Problem | Lösung |
|---------|--------|
| PyInstaller fehlt | `install_deps.bat` ausführen |
| Build-Fehler | `clean.bat` und dann neu builden |
| Exe startet nicht | `test.bat` für Diagnose |
| Fehlende Dateien | Pfade in `SWLegion.spec` prüfen |

---

**Bereit zum Kompilieren:** Führen Sie `install_deps.bat` aus, dann `build.bat`!