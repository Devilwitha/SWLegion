# Star Wars Legion: All-in-One Tool Suite

Dieses Projekt bietet eine Sammlung von digitalen Werkzeugen für das Tabletop-Spiel **Star Wars: Legion**. Es unterstützt Spieler beim Erstellen von Armeen, Generieren von Missionen und dient als digitaler Begleiter während des Spiels (inklusive AI-Gegner-Modus).

## Voraussetzungen

*   Python 3.x muss installiert sein.
*   Die `tkinter`-Bibliothek (standardmäßig in Python enthalten).

## Installation & Start

1.  Lade alle Dateien in einen Ordner.
2.  Starte das Hauptmenü mit folgendem Befehl:

```bash
python3 MainMenu.py
```

Von hier aus können alle drei Module gestartet werden.

---

## Die Module

### 1. Custom Unit Creator (`CustomUnitCreator.py`)
Ein mächtiges Werkzeug, um eigene Einheiten zu entwerfen und in das Spiel zu integrieren.
*   **Funktionen:**
    *   Erstellen komplett eigener Einheiten mit individuellen Werten (HP, Mut, Geschwindigkeit, etc.).
    *   Definition eigener Waffen mit Reichweite, Würfeln und Keywords.
    *   Zuordnung der Einheit zu einer oder mehreren Fraktionen.
    *   Die erstellten Einheiten stehen automatisch im **Armee Builder** zur Verfügung.

### 2. Armee Builder (`ArmeeBuilder.py`)
Ein Tool zum Erstellen und Speichern von Armeelisten.
*   **Funktionen:**
    *   Wahl der Fraktion (Imperium, Rebellen, Republik, Separatisten, Schattenkollektiv).
    *   Zugriff auf alle offiziellen Einheiten sowie **eigene Custom-Einheiten**.
    *   Hinzufügen von Einheiten und Ausrüstungskarten.
    *   Automatische Punkteberechnung.
    *   **Speichern/Laden:** Listen werden als `.json`-Dateien im Ordner `Armeen/` gespeichert.

### 3. Mission Generator (`MissionBuilder.py`)
Ein Tool, um zufällige oder spezifische Missions-Prompts zu erstellen (z.B. für ChatGPT oder als Inspiration).
*   **Funktionen:**
    *   Wahl der beteiligten Fraktionen.
    *   Wahl des Geländes (Wüste, Wald, Stadt, etc.).
    *   Generiert einen detaillierten Text mit Missionszielen und Sonderregeln.

### 4. Spiel-Begleiter & AI Simulator (`GameCompanion.py`)
Das Herzstück für das aktive Spiel. Es ersetzt Marker und Würfel und bietet einen Solo-Modus.
*   **Vorbereitung:**
    *   Lade deine Armeeliste (erstellt mit dem Armee Builder) über den blauen Button.
    *   Optional: Lade eine Gegner-Liste über den roten Button (für AI-Spiel).
*   **Spielablauf:**
    *   Klicke auf **"SPIEL STARTEN"**.
    *   **Befehl ziehen:** Der "Order Pool" wird automatisch gemischt. Klicke auf "BEFEHL ZIEHEN", um die nächste Einheit zu aktivieren.
    *   **AI-Modus:** Wenn "AI Aktiv" angehakt ist, zeigt das Tool bei Aktivierung einer Gegner-Einheit an, was diese tun möchte (z.B. "Bewegung in Deckung -> Angriff").
*   **Kampf-Simulator:**
    *   Klicke auf **"ANGRIFF"**, wenn eine Einheit aktiv ist.
    *   Wähle Waffen, Ziel, Deckung und Marker.
    *   Das Tool würfelt automatisch Angriff (Rot/Schwarz/Weiß) und Verteidigung, berechnet Treffer, Surges, Pierce und zeigt den finalen Schaden an.
    *   Schaden kann direkt auf die Zieleinheit angewendet werden.

## Dateien
*   `MainMenu.py`: Das Startmenü.
*   `CustomUnitCreator.py`: Editor für eigene Einheiten.
*   `ArmeeBuilder.py`: Editor für Listen.
*   `MissionBuilder.py`: Generator für Missionen.
*   `GameCompanion.py`: Das Spiel-Tool.
*   `LegionData.py`: Zentrale Datenbank mit allen Einheitenwerten (Geschwindigkeit, Würfel, etc.).
