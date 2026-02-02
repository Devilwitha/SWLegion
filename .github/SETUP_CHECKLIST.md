# GitHub Actions Setup Checkliste

## ✅ Setup-Schritte

### 1. Repository Setup
- [ ] Repository auf GitHub erstellen/pushen
- [ ] Workflows-Ordner `.github/workflows/` vorhanden
- [ ] Workflow-Dateien committed

### 2. Repository Einstellungen
- [ ] **Settings** → **Actions** → **General**:
  - [x] Allow all actions and reusable workflows
- [ ] **Settings** → **Actions** → **Workflow permissions**:
  - [x] Read and write permissions
  - [x] Allow GitHub Actions to create and approve pull requests

### 3. Secrets (Optional)
Aktuell benötigt: **Keine besonderen Secrets**
- GitHub Token wird automatisch bereitgestellt (`secrets.GITHUB_TOKEN`)

### 4. Erste Verwendung

#### Automatischer Build bei Tag:
```bash
git tag v1.0.0
git push origin v1.0.0
```

#### Manueller Build:
1. Gehe zu **Actions** Tab
2. Wähle **Manual Build**
3. Klicke **Run workflow**
4. Wähle Optionen und starte

## 📁 Erstellte Dateien

```
.github/
├── workflows/
│   ├── build-and-release.yml      # Automatische Builds & Releases
│   └── manual-build.yml           # Manuelle Builds mit Optionen
├── WORKFLOWS.md                   # Workflow-Dokumentation
└── SETUP_CHECKLIST.md            # Diese Datei
```

## 🔧 Workflow-Features

### build-and-release.yml
- ✅ Trigger bei Push/Tag/PR
- ✅ Python 3.11 Setup
- ✅ Dependency Caching
- ✅ PyInstaller Build
- ✅ Inno Setup Installation
- ✅ Installer-Erstellung
- ✅ Artifact Upload
- ✅ Automatische Releases bei Tags
- ✅ Build-Verifikation

### manual-build.yml
- ✅ Manuelle Trigger-Optionen
- ✅ Build-Typ Auswahl (Installer/Portable/Both)
- ✅ Draft Release Option
- ✅ Flexible Konfiguration

## 🚦 Testing

### Lokaler Test der Build-Scripts:
```bash
# Test build.bat
cd build/Win
.\build.bat

# Test Inno Setup (wenn installiert)
iscc SWLegion_Setup.iss

# Test Portable Package
.\create_portable_package.bat
```

### GitHub Actions Test:
1. Kleinen Commit machen
2. Push zu main/master
3. Actions Tab prüfen
4. Build-Logs überprüfen

## 📊 Erwartete Outputs

### Bei erfolgreichem Build:
- **Artifacts**: `SWLegion-Build-{sha}` (30 Tage)
- **Installer**: `SWLegion-Installer-{sha}` (90 Tage)

### Bei Tag-Release:
- **GitHub Release** mit:
  - `SWLegion_Installer.exe`
  - Release Notes
  - Download-Statistiken

### Bei manuellem Build:
- **Configurable Artifacts**
- **Optional Draft Release**

## 🐛 Häufige Probleme

### "Build failed: SWLegion.exe not found"
- Prüfe `build.bat` Pfade
- Kontrolliere Python Dependencies
- Überprüfe PyInstaller .spec Datei

### "Installer creation failed"
- Inno Setup Installation prüfen
- .iss Datei Syntax überprüfen
- Pfade in .iss kontrollieren

### "Release creation failed"
- Repository Permissions prüfen
- GITHUB_TOKEN Berechtigungen
- Tag-Format kontrollieren (v*)

## 📈 Monitoring

### Build Status anzeigen:
```markdown
![Build Status](https://github.com/USERNAME/SWLegion/actions/workflows/build-and-release.yml/badge.svg)
```

### Release Info:
```markdown
![Latest Release](https://img.shields.io/github/v/release/USERNAME/SWLegion)
![Downloads](https://img.shields.io/github/downloads/USERNAME/SWLegion/total)
```

## 🔄 Wartung

### Workflow Updates:
- Python Version upgraden
- Dependencies aktualisieren  
- Inno Setup Version ändern
- Build-Optionen anpassen

### Performance:
- Dependency Caching optimieren
- Build-Zeit reduzieren
- Artifact-Größe minimieren