# GitHub Actions Workflows

Dieses Repository enthält automatisierte Build- und Release-Workflows für Star Wars Legion Tool Suite.

## 🔄 Verfügbare Workflows

### Build and Release with Installer (`build-release-installer.yml`)
**Haupt-Workflow** der ausgelöst wird bei:
- Push zu `main`/`master` Branch
- Erstellung von Tags (v1.0, v1.1, etc.)
- Pull Requests
- Manueller Trigger

**Funktionen:**
- ✅ Automatische PyInstaller Build-Erstellung
- ✅ Inno Setup Installation via Chocolatey  
- ✅ Windows Installer (.exe) Generierung
- ✅ Artifact-Upload für Downloads
- ✅ Automatische GitHub Releases bei Tags
- ✅ Umfangreiche Build-Verifikation

## 🚀 Verwendung

### Automatische Releases
1. Tag erstellen: `git tag v1.0.0`
2. Tag pushen: `git push origin v1.0.0`
3. GitHub Actions erstellt automatisch:
   - PyInstaller Build
   - Windows Installer mit Inno Setup
   - GitHub Release mit Download-Links

### Manuelle Builds
1. Gehe zu **Actions** → **Build and Release with Installer**
2. Klicke **"Run workflow"**
3. Wähle Branch aus
4. Workflow startet automatisch

## 📦 Build-Ausgaben

### Installer (`SWLegion_Installer.exe`)
- Vollständiger Windows-Installer
- Automatische Deinstallation
- Start-Menü Integration
- Desktop-Verknüpfung (optional)

### Portable (`SWLegion_Portable.zip`)
- Keine Installation erforderlich
- Entpacken und ausführen
- `Start_SWLegion.bat` Launcher

## 🔧 Systemanforderungen

### GitHub Actions Runner:
- Windows Server 2022 (windows-latest)
- Python 3.11
- Inno Setup 6

### Build-Abhängigkeiten:
- PyInstaller
- PIL/Pillow
- tkinter
- Alle requirements.txt Pakete

## 📋 Workflow-Schritte

```mermaid
graph TD
    A[Code Checkout] --> B[Python Setup]
    B --> C[Dependencies Install]
    C --> D[Inno Setup Install]
    D --> E[PyInstaller Build]
    E --> F{Build Success?}
    F -->|Yes| G[Create Installer]
    F -->|No| H[Fail Build]
    G --> I[Upload Artifacts]
    I --> J{Tag Release?}
    J -->|Yes| K[Create GitHub Release]
    J -->|No| L[Store Artifacts]
```

## 🔐 Sicherheit

### Ausgeschlossene Dateien:
- ❌ `gemini_key.txt` (API Keys)
- ❌ Persönliche Konfigurationsdateien
- ✅ Alle Spiel-Daten und Assets enthalten

### Berechtigungen:
- 📖 Repository lesen
- 📝 Releases erstellen
- 🔄 Artifacts uploaden

## 📊 Artifact-Aufbewahrung

| Typ | Aufbewahrung | Beschreibung |
|-----|--------------|--------------|
| Build Artifacts | 30 Tage | PyInstaller Output |
| Installer | 90 Tage | Windows .exe Installer |
| Releases | Permanent | Tagged Releases |

## 🐛 Troubleshooting

### Build fehlschlägt:
1. Prüfe Python-Dependencies in `requirements.txt`
2. Kontrolliere PyInstaller .spec Konfiguration
3. Überprüfe Inno Setup .iss Syntax

### Installer-Erstellung fehlschlägt:
1. Prüfe Build-Output in `dist/SWLegion/`
2. Kontrolliere .iss Pfade
3. Überprüfe Inno Setup Installation

### Release nicht erstellt:
1. Prüfe Tag-Format (`v*`)
2. Kontrolliere GitHub Token-Berechtigungen
3. Überprüfe Repository-Settings