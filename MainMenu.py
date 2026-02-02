import tkinter as tk
from tkinter import messagebox
import os
import sys
import subprocess
import logging
from PIL import Image, ImageTk
from utilities import LegionUtils
pversion = "1.0v"
rversion = "2.5v"

class MainMenu:
    def __init__(self, root):
        LegionUtils.setup_logging()
        self.root = root
        self.root.title("Star Wars Legion: All-in-One Tool")
        self.root.geometry("400x700")
        
        # Set window icon
        try:
            icon_img = Image.open("bilder/SW_legion_logo.png")
            icon_img = icon_img.resize((32, 32), Image.Resampling.LANCZOS)
            self.icon_photo = ImageTk.PhotoImage(icon_img)
            self.root.iconphoto(True, self.icon_photo)
        except:
            pass  # Fallback if icon loading fails
        
        # Load and display logo
        try:
            logo_img = Image.open("bilder/SW_legion_logo.png")
            logo_img = logo_img.resize((300, 150), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            tk.Label(self.root, image=self.logo_photo).pack(pady=20)
        except Exception as e:
            # Fallback text if image loading fails
            tk.Label(self.root, text="Star Wars Legion Zentrale", font=("Segoe UI", 16, "bold")).pack(pady=20)

        btn_factory = tk.Button(self.root, text="Custom Factory", command=self.run_custom_factory, width=30, height=2, bg="#9C27B0", fg="white", font=("Segoe UI", 10, "bold"))
        btn_factory.pack(pady=10)

        btn_army = tk.Button(self.root, text="Armee Builder", command=self.run_army_builder, width=30, height=2, bg="#2196F3", fg="white", font=("Segoe UI", 10, "bold"))
        btn_army.pack(pady=10)

        btn_mission = tk.Button(self.root, text="Mission Generator", command=self.run_mission_builder, width=30, height=2, bg="#FF9800", fg="white", font=("Segoe UI", 10, "bold"))
        btn_mission.pack(pady=10)

        btn_game = tk.Button(self.root, text="Spiel-Begleiter (Game Companion)", command=self.run_game_companion, width=30, height=2, bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"))
        btn_game.pack(pady=10)

        # Separator line
        separator = tk.Frame(self.root, height=2, bd=1, relief=tk.SUNKEN)
        separator.pack(fill=tk.X, padx=40, pady=10)

        btn_howto = tk.Button(self.root, text="How To - Anleitung", command=self.show_howto, width=30, height=2, bg="#607D8B", fg="white", font=("Segoe UI", 10, "bold"))
        btn_howto.pack(pady=5)

        btn_about = tk.Button(self.root, text="About - Über das Programm", command=self.show_about, width=30, height=2, bg="#795548", fg="white", font=("Segoe UI", 10, "bold"))
        btn_about.pack(pady=5)

        tk.Label(self.root, text="Wähle ein Modul um zu starten.", font=("Segoe UI", 10)).pack(pady=20)

    def run_custom_factory(self):
        self.launch_script(os.path.join("utilities", "CustomFactoryMenu.py"))

    def run_army_builder(self):
        self.launch_script(os.path.join("utilities", "ArmeeBuilder.py"))

    def run_mission_builder(self):
        self.launch_script(os.path.join("utilities", "MissionBuilder.py"))

    def run_game_companion(self):
        self.launch_script(os.path.join("utilities", "GameCompanion.py"))

    def launch_script(self, script_name):
        try:
            # Prüfen ob Datei existiert
            if not os.path.exists(script_name):
                 logging.error(f"Script missing: {script_name}")
                 messagebox.showerror("Fehler", f"Datei nicht gefunden: {script_name}")
                 return

            # subprocess.Popen erlaubt paralleles Ausführen ohne die GUI einzufrieren
            logging.info(f"Launching submodule: {script_name}")

            # Use module execution if in utilities folder
            if script_name.startswith("utilities") and script_name.endswith(".py"):
                module_name = script_name.replace(os.sep, ".").replace(".py", "")
                cmd = [sys.executable, "-m", module_name]
            else:
                cmd = [sys.executable, script_name]

            subprocess.Popen(cmd)

        except Exception as e:
            logging.error(f"Failed to launch {script_name}: {e}")
            messagebox.showerror("Fehler", f"Konnte {script_name} nicht starten:\n{e}")

    def show_about(self):
        global pversion, rversion
        about_window = tk.Toplevel(self.root)
        about_window.title("Über Star Wars Legion Tool Suite")
        about_window.geometry("450x500")
        about_window.resizable(False, False)
        
        # Set window icon
        try:
            icon_img = Image.open("bilder/SW_legion_logo.png")
            icon_img = icon_img.resize((32, 32), Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_img)
            about_window.iconphoto(True, icon_photo)
        except:
            pass
        
        # Logo in About window
        try:
            logo_img = Image.open("bilder/SW_legion_logo.png")
            logo_img = logo_img.resize((150, 75), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            tk.Label(about_window, image=logo_photo).pack(pady=10)
            # Keep reference to prevent garbage collection
            about_window.logo_photo = logo_photo
        except:
            tk.Label(about_window, text="Star Wars Legion", font=("Segoe UI", 16, "bold")).pack(pady=10)
        
        # About text
        about_text = (
            "Star Wars Legion: All-in-One Tool Suite\n\n"
            "Code by BolliSoft (Nico Bollhalder)\n\n"
            f"Programm Version: {pversion}\n"
            f"Regelwerk: {rversion}\n\n"
            "Github: https://github.com/Devilwitha/SWLegion\n\n"
            "Eine umfassende Sammlung von Tools für\n"
            "Star Wars: Legion Tabletop Gaming"
        )
        
        tk.Label(about_window, text=about_text, font=("Segoe UI", 10), justify=tk.CENTER).pack(pady=20)
        
        tk.Button(about_window, text="Schließen", command=about_window.destroy, bg="#f44336", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)

    def show_howto(self):
        howto_window = tk.Toplevel(self.root)
        howto_window.title("How To - Anleitung")
        howto_window.geometry("700x600")
        
        # Set window icon
        try:
            icon_img = Image.open("bilder/SW_legion_logo.png")
            icon_img = icon_img.resize((32, 32), Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_img)
            howto_window.iconphoto(True, icon_photo)
        except:
            pass
        
        # Scrollable text area
        frame = tk.Frame(howto_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, font=("Segoe UI", 10), padx=10, pady=10)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # How-to content
        howto_content = """
Star Wars Legion Tool Suite - Anleitung

=== EMPFOHLENE REIHENFOLGE ===

1. CUSTOM FACTORY
   • Erstelle eigene Einheiten, Kommandokarten und Schlachtkarten
   • Erweitere das Spiel mit benutzerdefinierten Inhalten
   • Nutze dies zuerst, um deine gewünschten Inhalte zu erstellen

2. ARMEE BUILDER
   • Baue deine Armee aus verfügbaren Einheiten
   • Wähle Kommandokarten (7 Karten Deck)
   • Exportiere deine fertige Armee für den Game Companion
   • WICHTIG: Speichere deine Armee für den nächsten Schritt!

3. MISSION GENERATOR
   • Erstelle zufällige oder spezifische Missionen
   • Nutze die AI-Generierung für detaillierte Szenarien
   • Wähle Fraktionen, Gelände und Missionsziele
   • Speichere deine Mission für das Spiel

4. SPIEL-BEGLEITER (GAME COMPANION)
   • Lade deine erstellte Mission
   • Importiere deine Armeen
   • Nutze den Kampf-Simulator und AI-Gegner
   • Verfolge Rundenabläufe und Spielzustand

=== DETAILLIERTE MODULE-BESCHREIBUNG ===

CUSTOM FACTORY:
• Einheiten-Editor: Erstelle eigene Truppen mit Statistiken
• Karten-Editor: Designe Kommando- und Schlachtkarten
• Waffen-Editor: Definiere neue Bewaffnung
• Keyword-System: Füge Spezialfähigkeiten hinzu

ARMEE BUILDER:
• Punkt-Management: Baue Armeen nach Punktlimit
• Rang-Beschränkungen: Automatische Validierung der Armee-Komposition
• Ausrüstungs-System: Wähle Upgrades und Ausrüstung
• Export-Funktion: Speichere für Game Companion

MISSION GENERATOR:
• Standard-Missionen: Vorgefertigte Szenarien
• AI-Generator: Automatische Mission-Erstellung via Gemini AI
• Karten-Visualisierung: Interaktive Schlachtfeld-Anzeige
• Fraktions-Auswahl: Alle verfügbaren Fraktionen

GAME COMPANION:
• Rundenmanagement: Automatische Phasen-Verfolgung
• Kampf-Simulator: Würfel-Engine mit automatischer Schadensberechnung
• AI-Gegner: Intelligent handelnde Computer-Gegner
• Zustandsverfolgung: HP, Marker, Aktivierungen

=== TIPPS ===

• Starte immer mit einer gespeicherten Mission im Game Companion
• Verwende die AI-Generierung für abwechslungsreiche Szenarien
• Experimentiere mit Custom Factory für einzigartige Spielerfahrungen
• Der Game Companion kann auch ohne vollständige Armeen für Kampf-Tests genutzt werden

=== SYSTEMVORAUSSETZUNGEN ===

• Python 3.8+
• PIL (Pillow) für Bildverarbeitung
• tkinter (meist standardmäßig installiert)
• Optional: requests für AI-Generierung
"""
        
        text_widget.insert("1.0", howto_content)
        text_widget.config(state=tk.DISABLED)
        
        tk.Button(howto_window, text="Schließen", command=howto_window.destroy, bg="#f44336", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()
