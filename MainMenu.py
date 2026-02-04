import tkinter as tk
from tkinter import messagebox
import os
import sys
import subprocess
import logging
from PIL import Image, ImageTk

# Fix imports for PyInstaller executable
if getattr(sys, 'frozen', False):
    # Running as PyInstaller executable
    sys.path.append(os.path.dirname(sys.executable))
    from utilities import LegionUtils
else:
    # Running as Python script  
    from utilities import LegionUtils

pversion = "2.0v"
rversion = "2.5v"

class MainMenu:
    def __init__(self, root):
        LegionUtils.setup_logging()
        self.root = root
        self.root.title("Star Wars Legion: All-in-One Tool  {pversion} (Rules {rversion})".format(pversion=pversion, rversion=rversion))
        self.root.geometry("400x700")
        
        # Set window icon
        try:
            # Get resource path for executable
            if getattr(sys, 'frozen', False):
                # Running as executable
                base_path = sys._MEIPASS  # PyInstaller temp directory
            else:
                # Running as script
                base_path = os.path.dirname(os.path.abspath(__file__))
                
            icon_path_png = os.path.join(base_path, "bilder", "SW_legion_logo.png")
            icon_path_ico = os.path.join(base_path, "bilder", "SW_legion_logo.ico")
            
            # Prefer .ico for Windows title bar
            if os.path.exists(icon_path_ico):
                self.root.iconbitmap(icon_path_ico)
            
            # Fallback/Additional for taskbar
            if os.path.exists(icon_path_png):
                icon_img = Image.open(icon_path_png)
                icon_img = icon_img.resize((32, 32), Image.Resampling.LANCZOS)
                self.icon_photo = ImageTk.PhotoImage(icon_img)
                self.root.iconphoto(True, self.icon_photo)
                
        except Exception as e:
            logging.warning(f"Could not load icon: {e}")
            pass  # Fallback if icon loading fails
        
        # Load and display logo
        try:
            # Path determined above
            logo_path = os.path.join(base_path, "bilder", "SW_legion_logo.png")
            
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
            else:
                # Fallback: create a simple placeholder
                logo_img = Image.new('RGB', (200, 100), color=(25, 25, 50))
                from PIL import ImageDraw
                draw = ImageDraw.Draw(logo_img)
                draw.text((50, 40), "SW LEGION", fill=(255, 255, 255))
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

        btn_music = tk.Button(self.root, text="🎵 Musik Player", command=self.run_music_player, width=30, height=2, bg="#E91E63", fg="white", font=("Segoe UI", 10, "bold"))
        btn_music.pack(pady=10)

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

    def run_music_player(self):
        """Öffne den Musik Player"""
        try:
            logging.info("Opening Music Player")
            from utilities.MusicPlayer import MusicPlayer
            new_window = tk.Toplevel()
            new_window.withdraw()
            app = MusicPlayer(new_window)
            new_window.deiconify()
            logging.info("Music Player opened successfully")
        except Exception as e:
            error_msg = f"Failed to open Music Player: {str(e)}"
            logging.error(error_msg, exc_info=True)
            messagebox.showerror("Fehler", f"Konnte Musik Player nicht öffnen:\n\n{str(e)}\n\nStelle sicher dass pygame installiert ist.")

    def launch_script(self, script_name):
        try:
            logging.info(f"Launching submodule: {script_name}")
            
            # Determine execution mode more reliably
            is_frozen = getattr(sys, 'frozen', False)
            has_meipass = hasattr(sys, '_MEIPASS')
            
            # For better compatibility, prefer direct imports when possible
            # This works in both script and executable mode
            logging.info(f"Execution mode - frozen: {is_frozen}, MEIPASS: {has_meipass}")
            
            # Always try direct import first (works in both modes)
            if self.try_direct_import(script_name):
                return
                
            # Fallback to subprocess for script mode only
            if not is_frozen and not has_meipass:
                logging.info(f"Fallback to subprocess for {script_name}")
                # Check if file exists
                if not os.path.exists(script_name):
                     error_msg = f"Script missing: {script_name}"
                     logging.error(error_msg)
                     messagebox.showerror("Fehler", f"Datei nicht gefunden: {script_name}")
                     return

                cmd = [sys.executable, script_name]
                logging.info(f"Executing subprocess command: {cmd}")
                subprocess.Popen(cmd)
            else:
                # If we're in executable mode and direct import failed, show error
                raise ImportError(f"Could not import module for {script_name}")

        except Exception as e:
            error_msg = f"Failed to launch {script_name}: {str(e)}"
            logging.error(error_msg, exc_info=True)
            messagebox.showerror("Fehler", f"Konnte {script_name} nicht starten:\n\n{str(e)}\n\nSiehe Log für Details.")

    def try_direct_import(self, script_name):
        """Try to import and run modules directly. Returns True if successful, False otherwise."""
        try:
            # Normalize path for comparison
            script_name = script_name.replace('\\', '/')
            logging.info(f"Attempting direct module import for: {script_name}")
            
            if script_name == "utilities/GameCompanion.py":
                logging.info("Importing GameCompanion module")
                from utilities.GameCompanion import GameCompanion
                logging.info("GameCompanion import successful")
                new_window = tk.Toplevel()
                new_window.withdraw()  # Hide initially
                app = GameCompanion(new_window)
                new_window.deiconify()  # Show after setup
                logging.info("GameCompanion instance created successfully")
                return True
                
            elif script_name == "utilities/ArmeeBuilder.py":
                logging.info("Importing ArmeeBuilder module")
                from utilities.ArmeeBuilder import LegionArmyBuilder  # Correct class name
                logging.info("ArmeeBuilder import successful")
                new_window = tk.Toplevel()
                new_window.withdraw()
                app = LegionArmyBuilder(new_window)
                new_window.deiconify()
                logging.info("ArmeeBuilder instance created successfully")
                return True
                
            elif script_name == "utilities/MissionBuilder.py":
                logging.info("Importing MissionBuilder module")
                from utilities.MissionBuilder import LegionMissionGenerator  # Correct class name
                logging.info("MissionBuilder import successful")
                new_window = tk.Toplevel()
                new_window.withdraw()
                app = LegionMissionGenerator(new_window)
                new_window.deiconify()
                logging.info("MissionBuilder instance created successfully")
                return True
                
            elif script_name == "utilities/CustomFactoryMenu.py":
                logging.info("Importing CustomFactoryMenu module")
                from utilities.CustomFactoryMenu import CustomFactoryMenu
                logging.info("CustomFactoryMenu import successful")
                new_window = tk.Toplevel()
                new_window.withdraw()
                app = CustomFactoryMenu(new_window)
                new_window.deiconify()
                logging.info("CustomFactoryMenu instance created successfully")
                return True
                
            elif script_name == "utilities/BattlefieldMapCreator.py":
                logging.info("Importing BattlefieldMapCreator module")
                from utilities.BattlefieldMapCreator import BattlefieldMapCreator
                logging.info("BattlefieldMapCreator import successful")
                new_window = tk.Toplevel()
                new_window.withdraw()
                app = BattlefieldMapCreator(new_window)
                new_window.deiconify()
                logging.info("BattlefieldMapCreator instance created successfully")
                return True
                
            elif script_name == "utilities/CardPrinter.py":
                logging.info("Importing CardPrinter module")
                from utilities.CardPrinter import CardPrinter
                logging.info("CardPrinter import successful")
                new_window = tk.Toplevel()
                new_window.withdraw()
                app = CardPrinter(new_window)
                new_window.deiconify()
                logging.info("CardPrinter instance created successfully")
                return True
                
            elif script_name == "utilities/CustomUnitCreator.py":
                logging.info("Importing CustomUnitCreator module")
                from utilities.CustomUnitCreator import CustomUnitCreator
                logging.info("CustomUnitCreator import successful")
                new_window = tk.Toplevel()
                new_window.withdraw()
                app = CustomUnitCreator(new_window)
                new_window.deiconify()
                logging.info("CustomUnitCreator instance created successfully")
                return True
                
            elif script_name == "utilities/CustomUpgradeCreator.py":
                logging.info("Importing CustomUpgradeCreator module")
                from utilities.CustomUpgradeCreator import CustomUpgradeCreator
                logging.info("CustomUpgradeCreator import successful")
                new_window = tk.Toplevel()
                new_window.withdraw()
                app = CustomUpgradeCreator(new_window)
                new_window.deiconify()
                logging.info("CustomUpgradeCreator instance created successfully")
                return True
                
            elif script_name == "utilities/CustomBattleCardCreator.py":
                logging.info("Importing CustomBattleCardCreator module")
                from utilities.CustomBattleCardCreator import CustomBattleCardCreator
                logging.info("CustomBattleCardCreator import successful")
                new_window = tk.Toplevel()
                new_window.withdraw()
                app = CustomBattleCardCreator(new_window)
                new_window.deiconify()
                logging.info("CustomBattleCardCreator instance created successfully")
                return True
                
            elif script_name == "utilities/CustomCommandCardCreator.py":
                logging.info("Importing CustomCommandCardCreator module")
                from utilities.CustomCommandCardCreator import CustomCommandCardCreator
                logging.info("CustomCommandCardCreator import successful")
                new_window = tk.Toplevel()
                new_window.withdraw()
                app = CustomCommandCardCreator(new_window)
                new_window.deiconify()
                logging.info("CustomCommandCardCreator instance created successfully")
                return True
                
            else:
                # Module not configured for direct execution
                logging.warning(f"Module {script_name} not configured for direct execution")
                return False
                
        except Exception as e:
            error_msg = f"Error during direct import of {script_name}: {str(e)}"
            logging.error(error_msg, exc_info=True)
            return False

    def show_about(self):
        global pversion, rversion
        about_window = tk.Toplevel(self.root)
        about_window.title("Über Star Wars Legion Tool Suite")
        about_window.geometry("450x500")
        about_window.resizable(False, False)
        
        # Set window icon
        try:
            if getattr(sys, 'frozen', False):
                # Running as executable
                base_path = sys._MEIPASS
                icon_path = os.path.join(base_path, "bilder", "SW_legion_logo.png")
            else:
                # Running as script
                icon_path = "bilder/SW_legion_logo.png"
                
            icon_img = Image.open(icon_path)
            icon_img = icon_img.resize((32, 32), Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_img)
            about_window.iconphoto(True, icon_photo)
        except:
            pass
        
        # Logo in About window
        try:
            if getattr(sys, 'frozen', False):
                # Running as executable
                base_path = sys._MEIPASS
                logo_path = os.path.join(base_path, "bilder", "SW_legion_logo.png")
            else:
                # Running as script
                logo_path = "bilder/SW_legion_logo.png"
                
            logo_img = Image.open(logo_path)
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

=== NEU: MUSIK & LOGGING ===
• 🎵 Musik Player: Eigene Soundtracks für die Schlacht (im Hauptmenü)
• 💾 Battle Log: Automatische Speicherung aller Ereignisse im 'log'-Ordner

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
   • Lade deine erstellte Mission & Importiere deine Armeen
   • 🤖 AI-Gegner: "Vorschlag ausführen" lässt die AI komplexe Züge (z.B. Bewegen -> Angreifen) automatisch durchführen
   • ⚔️ Kampf-Simulator: Würfel-Engine mit automatischer Schadensberechnung, Deckung & Token-Management
   • 📝 Live-Log: Verfolge jeden Würfelwurf und jede Aktion im automatischen Battle-Log

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
• AI-Integration: Gemini analysiert das Schlachtfeld und schlägt taktische Züge vor
• Automatisierung: AI führt Befehle (Bewegen, Angreifen, Zielen) selbstständig aus
• Zustandsverfolgung: HP, Marker, Aktivierungen werden automatisch verwaltet

=== TIPPS ===

• Starte immer mit einer gespeicherten Mission im Game Companion
• Verwende die AI-Generierung für abwechslungsreiche Szenarien
• Experimentiere mit Custom Factory für einzigartige Spielerfahrungen
• Der Game Companion kann auch ohne vollständige Armeen für Kampf-Tests genutzt werden

=== SYSTEMVORAUSSETZUNGEN ===

• Python 3.8+
• PIL (Pillow) für Bildverarbeitung
• tkinter (meist standardmäßig installiert)
• Optional: google-genai für AI-Funktionen

=== AI SETUP (GEMINI) ===

• Um die AI zu nutzen, wird ein Google Gemini API Key benötigt.
• Erstelle eine Datei 'gemini_key.txt' im Hauptordner.
• Kopiere deinen API Key in diese Datei (einfach nur den Key, keine Leerzeichen).
• Ohne Key funktioniert der Game Companion nur im manuellen Modus.

=== PROBLEMLÖSUNG ===

• "Startet nicht": Überprüfe ob 'google-genai' im venv installiert ist (pip install -r requirements.txt).
• "Keine Musik": Stelle sicher, dass der 'musik'-Ordner .mp3 oder .wav Dateien enthält.
• "Log nicht erstellt": Der Ordner 'log' wird automatisch erstellt, benötigt aber Schreibrechte.
"""
        
        text_widget.insert("1.0", howto_content)
        text_widget.config(state=tk.DISABLED)
        
        tk.Button(howto_window, text="Schließen", command=howto_window.destroy, bg="#f44336", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()
