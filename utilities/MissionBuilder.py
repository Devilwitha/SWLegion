import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import random
import os
import sys
import subprocess

# Import LegionDatabase with compatibility for both script and package modes
try:
    from .LegionData import LegionDatabase
    from .LegionUtils import get_writable_path, get_gemini_key
    from .MapRenderer import MapRenderer
except ImportError:
    try:
        from utilities.LegionData import LegionDatabase
        from utilities.LegionUtils import get_writable_path, get_gemini_key
        from utilities.MapRenderer import MapRenderer
    except ImportError:
        from LegionData import LegionDatabase
        from LegionUtils import get_writable_path, get_gemini_key
        from MapRenderer import MapRenderer

from PIL import Image, ImageTk, ImageDraw, ImageFont

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Gemini SDK Setup
import logging
try:
    from google import genai
    GEMINI_AVAILABLE = True
    GEMINI_VERSION = 2
    logging.info("MissionBuilder: Using google-genai (v2) - SUCCESS")
except ImportError as e:
    logging.error(f"MissionBuilder: google-genai import failed: {e}")
    try:
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
        GEMINI_VERSION = 1
        logging.info("MissionBuilder: Using google.generativeai (v1) - SUCCESS")
    except ImportError as e2:
        logging.error(f"MissionBuilder: google.generativeai import failed: {e2}")
        GEMINI_AVAILABLE = False
        GEMINI_VERSION = 0

class LegionMissionGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("SW Legion: Mission & Map Generator")
        self.root.geometry("1400x1200")
        
        # Set window icon
        try:
            icon_img = Image.open("bilder/SW_legion_logo.png")
            icon_img = icon_img.resize((32, 32), Image.Resampling.LANCZOS)
            self.icon_photo = ImageTk.PhotoImage(icon_img)
            self.root.iconphoto(True, self.icon_photo)
        except:
            pass

        self.db = LegionDatabase()
        self.api_key = self.load_api_key()
        self.current_scenario_text = ""
        
        # Musik-Einstellungen
        self.music_enabled = False
        self.selected_playlist = None
        self.music_settings = self.load_music_settings()
        
        # --- Daten ---
        self.fraktionen = [
            "Galaktisches Imperium",
            "Rebellenallianz",
            "Galaktische Republik",
            "Separatistenallianz",
            "Schattenkollektiv (Shadow Collective)"
        ]
        
        self.gelaende_typen = [
            "Wald / Dschungel (z.B. Endor, Kashyyyk)",
            "Wüste (z.B. Tatooine, Geonosis)",
            "Schnee / Eis (z.B. Hoth)",
            "Stadt / Urban (z.B. Corellia, Jedha City)",
            "Industrie / Fabrik (z.B. Sullust)",
            "Gebirge / Felsen",
            "Innenraum / Raumstation (Skirmish)",
            "Sumpf"
        ]
        
        # Speicher für die Checkboxen
        self.var_fraktionen = {}
        self.var_gelaende = {}
        
        # Army Data
        self.blue_army = None
        self.red_army = None
        self.current_deployment = "Battle Lines"

        # GUI Elemente erstellen
        self.create_widgets()

    def create_widgets(self):
        # Split Window: Links Einstellungen, Rechts Map
        paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # --- LINKS: EINSTELLUNGEN ---
        frame_settings = tk.Frame(paned, width=400)
        paned.add(frame_settings)

        # 1. FRAKTIONEN
        lbl_frake = tk.Label(frame_settings, text="1. Beteiligte Armeen:", font=("Arial", 11, "bold"))
        lbl_frake.pack(anchor="w", pady=(0, 5))

        frame_fraktionen = tk.Frame(frame_settings, relief=tk.GROOVE, borderwidth=1)
        frame_fraktionen.pack(fill="x", pady=5)

        for frak in self.fraktionen:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(frame_fraktionen, text=frak, variable=var, anchor="w", command=self.update_faction_combos)
            chk.pack(fill="x", padx=5)
            self.var_fraktionen[frak] = var

        # 2. GELÄNDE / TERRAIN
        lbl_terrain = tk.Label(frame_settings, text="2. Gelände & Umgebung:", font=("Arial", 11, "bold"))
        lbl_terrain.pack(anchor="w", pady=(15, 5))

        frame_terrain = tk.Frame(frame_settings, relief=tk.GROOVE, borderwidth=1)
        frame_terrain.pack(fill="x", pady=5)

        for gelaende in self.gelaende_typen:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(frame_terrain, text=gelaende, variable=var, anchor="w", command=self.update_terrain_options)
            chk.pack(fill="x", padx=5)
            self.var_gelaende[gelaende] = var

        # Sarlacc Pit Option (nur bei Wüste sichtbar)
        self.frame_sarlacc = tk.Frame(frame_terrain)
        self.var_sarlacc_pit = tk.BooleanVar()
        self.chk_sarlacc = tk.Checkbutton(self.frame_sarlacc, text="🕳️ Sarlacc Pit vorhanden", variable=self.var_sarlacc_pit, anchor="w", fg="#8B4513")
        self.chk_sarlacc.pack(fill="x", padx=20)
        # Zunächst versteckt
        self.frame_sarlacc.pack_forget()

        # 3. PUNKTE
        lbl_punkte = tk.Label(frame_settings, text="3. Punktezahl:", font=("Arial", 11, "bold"))
        lbl_punkte.pack(anchor="w", pady=(15, 5))

        self.entry_punkte = tk.Entry(frame_settings, font=("Arial", 10))
        self.entry_punkte.insert(0, "800")
        self.entry_punkte.pack(fill="x", pady=5)
        
        # 3b. RUNDEN
        lbl_runden = tk.Label(frame_settings, text="Anzahl Runden:", font=("Arial", 11, "bold"))
        lbl_runden.pack(anchor="w", pady=(10, 5))
        
        self.entry_runden = tk.Entry(frame_settings, font=("Arial", 10))
        self.entry_runden.insert(0, "6")
        self.entry_runden.pack(fill="x", pady=5)

        # 3c. MUSIK EINSTELLUNGEN
        self.create_music_section(frame_settings)
        
        # 3d. AI & KAMERA (GEMINI)
        self.create_ai_section(frame_settings)

        # 4. BUTTON
        btn_gen = tk.Button(
            frame_settings,
            text="SZENARIO GENERIEREN (AI)",
            command=self.generate_scenario_with_gemini,
            bg="#2196F3", fg="white", font=("Arial", 12, "bold"), height=2
        )
        btn_gen.pack(pady=20, fill="x")

        # 5. VORSCHAU
        lbl_output = tk.Label(frame_settings, text="Szenario-Text:", font=("Arial", 9))
        lbl_output.pack(anchor="w")

        self.txt_output = tk.Text(frame_settings, height=8, font=("Consolas", 8), wrap="word")
        # Configure formatting tags
        self.txt_output.tag_configure("bold", font=("Consolas", 8, "bold"))
        self.txt_output.tag_configure("italic", font=("Consolas", 8, "italic"))
        self.txt_output.pack(fill="both", expand=True)

        # --- RECHTS: MAP VISUALISIERUNG ---
        frame_map = tk.Frame(paned, bg="#eee", padx=10, pady=10)
        paned.add(frame_map)

        tk.Label(frame_map, text="Aufstellung & Schlachtfeld", font=("Segoe UI", 16, "bold"), bg="#eee").pack(pady=10)

        # Canvas
        self.canvas_width = 500
        self.canvas_height = 800 # 6x3 feet -> 2:1 ratio approx (90x180cm). In pixels: 400x800 vertical or 800x400 horiz.
        # Let's do horizontal 800x400
        self.canvas_width = 800
        self.canvas_height = 400

        self.canvas = tk.Canvas(frame_map, width=self.canvas_width, height=self.canvas_height, bg="#81d4fa") # Blue field
        self.canvas.pack(pady=10)

        tk.Label(frame_map, text="Blau = Spielfeld | Rot = Aufstellungszone", bg="#eee").pack()

        # Deployment Controls
        frame_deploy_ctrl = tk.Frame(frame_map, bg="#eee")
        frame_deploy_ctrl.pack(fill="x", pady=10)

        # Load values from DB + Hardcoded defaults
        self.default_deployments = [
            "Battle Lines", "The Long March", "Disarray", "Major Offensive", "Danger Close", "Hemmed In",
            "Hinterhalt (Ambush)", "Einkesselung (Encirclement)", "Nahkampf (Close Quarters)"
        ]

        self.default_missions = [
            "Kein Marker",
            "Abfangen (Intercept)",
            "Schlüsselpositionen (Key Positions)",
            "Durchbruch (Breakthrough)",
            "Eliminierung (Deathmatch)",
            "Evakuierung (Hostage)",
            "Vorräte bergen (Recover Supplies)",
            "Sabotage"
        ]

        # Fetch custom cards
        custom_deploy = [c["name"] for c in self.db.battle_cards if c.get("category") == "Deployment"]
        custom_mission = [c["name"] for c in self.db.battle_cards if c.get("category") == "Objective"]

        all_deploy = self.default_deployments + custom_deploy
        all_mission = self.default_missions + custom_mission

        tk.Label(frame_deploy_ctrl, text="Aufstellung:", bg="#eee").pack(side="left")
        self.combo_deploy = ttk.Combobox(frame_deploy_ctrl, values=all_deploy, state="readonly", width=25)
        self.combo_deploy.current(0)
        self.combo_deploy.pack(side="left", padx=5)
        self.combo_deploy.bind("<<ComboboxSelected>>", self.update_map)

        # Mission / Objective Control
        tk.Label(frame_deploy_ctrl, text="Mission:", bg="#eee").pack(side="left", padx=(10,0))
        self.combo_mission = ttk.Combobox(frame_deploy_ctrl, values=all_mission, state="readonly", width=25)
        self.combo_mission.current(0)
        self.combo_mission.pack(side="left", padx=5)
        self.combo_mission.bind("<<ComboboxSelected>>", self.update_map)

        tk.Button(frame_deploy_ctrl, text="Zufällig", command=self.random_deploy, bg="#FF9800", fg="white").pack(side="left", padx=5)

        # Faction Assignment
        frame_armies = tk.Frame(frame_map, bg="#eee")
        frame_armies.pack(fill="x", pady=10)

        # Blue Faction Selector
        f_blue = tk.Frame(frame_armies, bg="#eee")
        f_blue.pack(side="left", padx=10)
        tk.Label(f_blue, text="Fraktion BLAU (Spieler)", fg="blue", bg="#eee", font=("bold")).pack()
        self.combo_blue = ttk.Combobox(f_blue, state="readonly", width=30)
        self.combo_blue.pack()
        self.combo_blue.bind("<<ComboboxSelected>>", self.update_map)

        # Red Faction Selector
        f_red = tk.Frame(frame_armies, bg="#eee")
        f_red.pack(side="right", padx=10)
        tk.Label(f_red, text="Fraktion ROT (Gegner)", fg="red", bg="#eee", font=("bold")).pack()
        self.combo_red = ttk.Combobox(f_red, state="readonly", width=30)
        self.combo_red.pack()
        self.combo_red.bind("<<ComboboxSelected>>", self.update_map)

        # Save Mission & Launch Creator
        btn_frame = tk.Frame(frame_map, bg="#eee")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="� Mission Laden", command=self.load_mission, bg="#FF9800", fg="white", font=("bold", 12)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="�💾 Mission Speichern", command=self.save_mission, bg="#4CAF50", fg="white", font=("bold", 12)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="🎮 Spiel starten", command=self.start_game, bg="#2196F3", fg="white", font=("bold", 12)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="✏ Schlachtfeld-Planer öffnen", command=self.launch_map_creator, bg="#9C27B0", fg="white", font=("bold", 12)).pack(side=tk.LEFT, padx=10)

        # Draw Initial
        self.update_map()

    def launch_map_creator(self):
        script_name = os.path.join("utilities", "BattlefieldMapCreator.py")
        if os.path.exists(script_name):
            subprocess.Popen([sys.executable, script_name])
        else:
            messagebox.showerror("Fehler", "BattlefieldMapCreator.py nicht gefunden.")

    def start_game(self):
        """Lädt eine gespeicherte Mission und startet das Spiel mit Musik"""
        from tkinter import filedialog
        try:
            initial_dir = get_writable_path("Missions")
            file_path = filedialog.askopenfilename(
                initialdir=initial_dir,
                title="Mission zum Starten auswählen",
                filetypes=[("JSON", "*.json")]
            )
            
            if file_path:
                # Ermittle den Pfad zu GameCompanion.py relativ zum aktuellen Script
                current_dir = os.path.dirname(os.path.abspath(__file__))
                # Falls MissionBuilder in utilities liegt:
                script_path = os.path.join(current_dir, "GameCompanion.py")
                
                if not os.path.exists(script_path):
                     # Falls wir nicht in utilities sind, versuche absoluten Pfad zu rekonstruieren
                     # Das hier ist ein Fallback
                     script_path = os.path.abspath(os.path.join("utilities", "GameCompanion.py"))

                if os.path.exists(script_path):
                    # Starte GameCompanion als separaten Prozess mit dem Missions-Pfad als Argument
                    subprocess.Popen([sys.executable, script_path, file_path])
                else:
                    messagebox.showerror("Fehler", f"GameCompanion nicht gefunden unter:\n{script_path}")
                    
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Starten des Spiels: {e}")

    def random_deploy(self):
        # Update values in case custom ones changed (simplified)
        vals_d = self.combo_deploy['values']
        vals_m = self.combo_mission['values']

        self.combo_deploy.set(random.choice(vals_d))
        self.combo_mission.set(random.choice(vals_m))

        self.update_map()

    def update_faction_combos(self):
        # Get selected factions from checkboxes
        selected = [f for f, var in self.var_fraktionen.items() if var.get()]

        # Get list of army files for these factions?
        # User requirement: "anstelle von armee laden nim lieber die beteiligten armeen"
        # Simplification: Allow selecting the *Faction* itself to assign to a side.
        # GameCompanion will then load from that Faction folder.

        # Populate Comboboxes
        self.combo_blue['values'] = selected
        self.combo_red['values'] = selected

        if selected:
            if not self.combo_blue.get(): self.combo_blue.current(0)
            if len(selected) > 1 and not self.combo_red.get(): self.combo_red.current(1)
            elif not self.combo_red.get(): self.combo_red.current(0)

        self.update_map()

    def update_terrain_options(self):
        """Zeigt/versteckt Sarlacc Pit Option basierend auf Wüste-Auswahl."""
        wueste_key = "Wüste (z.B. Tatooine, Geonosis)"
        if wueste_key in self.var_gelaende and self.var_gelaende[wueste_key].get():
            self.frame_sarlacc.pack(fill="x", padx=5)
        else:
            self.frame_sarlacc.pack_forget()
            self.var_sarlacc_pit.set(False)  # Reset wenn Wüste abgewählt

    def load_api_key(self):
        # Try to load from file
        key = get_gemini_key()
        return key if key else ""

    def insert_formatted_text(self, text_widget, content):
        """Simple formatting: Bold titles and bullet points"""
        text_widget.delete("1.0", tk.END)
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                text_widget.insert(tk.END, '\n')
                continue
            
            # Check if it's a title (ends with : or contains **text**)
            is_title = False
            if line.endswith(':') or '**' in line:
                is_title = True
            
            # Remove ** markers if present
            clean_line = line.replace('**', '')
            
            # Check if it's a bullet point (starts with * or numbered)
            is_bullet = line.startswith('*') or line.startswith('-') or (len(line) > 2 and line[0].isdigit() and line[1] == '.')
            
            # Format the line
            if is_title:
                # Insert as bold title
                start_pos = text_widget.index(tk.END)
                text_widget.insert(tk.END, clean_line)
                end_pos = text_widget.index(tk.END)
                text_widget.tag_add("bold", start_pos, end_pos)
            elif is_bullet:
                # Convert to bullet point with -
                if line.startswith('*'):
                    bullet_text = '- ' + line[1:].strip()
                elif line.startswith('-'):
                    bullet_text = line
                elif line[0].isdigit() and line[1] == '.':
                    bullet_text = '- ' + line[2:].strip()
                else:
                    bullet_text = '- ' + line
                text_widget.insert(tk.END, bullet_text)
            else:
                # Regular text
                text_widget.insert(tk.END, clean_line)
            
            text_widget.insert(tk.END, '\n')

    def generate_map_image(self):
        """Generates a PIL Image of the current map for saving using MapRenderer"""
        try:
            # Generate Base Map
            img = MapRenderer.draw_map(self.combo_deploy.get(), db=self.db)
            
            # Add Overlays
            img = MapRenderer.draw_overlays(
                img, 
                self.combo_mission.get(), 
                self.combo_blue.get(), 
                self.combo_red.get()
            )

            # Ensure directory exists
            map_dir = "images/maps"
            if not os.path.exists(map_dir):
                os.makedirs(map_dir, exist_ok=True)
                
            # Save file
            import uuid
            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.abspath(os.path.join(map_dir, filename))
            img.save(filepath)
            return filepath
            
        except Exception as e:
            logging.error(f"Failed to generate map image with MapRenderer: {e}")
            return ""

    def load_mission(self):
        """Lädt eine gespeicherte Mission und füllt alle Felder aus."""
        try:
            initial_dir = get_writable_path("Missions")
            file_path = filedialog.askopenfilename(
                initialdir=initial_dir,
                title="Mission laden",
                filetypes=[("JSON", "*.json")]
            )
            
            if not file_path:
                return
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logging.info(f"Loading mission from {file_path}")
            
            # 1. Fraktionen-Checkboxen zurücksetzen und setzen
            for var in self.var_fraktionen.values():
                var.set(False)
            
            # Fraktionen aus blue/red_faction ermitteln
            factions_to_select = set()
            if data.get("blue_faction"):
                factions_to_select.add(data["blue_faction"])
            if data.get("red_faction"):
                factions_to_select.add(data["red_faction"])
            
            for faction in factions_to_select:
                if faction in self.var_fraktionen:
                    self.var_fraktionen[faction].set(True)
            
            # Faction Combos aktualisieren
            self.update_faction_combos()
            
            # Blue/Red Faction setzen
            if data.get("blue_faction"):
                self.combo_blue.set(data["blue_faction"])
            if data.get("red_faction"):
                self.combo_red.set(data["red_faction"])
            
            # 2. Gelände-Checkboxen zurücksetzen und setzen
            for var in self.var_gelaende.values():
                var.set(False)
            
            terrain_list = data.get("terrain", [])
            for terrain in terrain_list:
                if terrain in self.var_gelaende:
                    self.var_gelaende[terrain].set(True)
            
            # Terrain-Optionen aktualisieren (Sarlacc Pit anzeigen falls Wüste)
            self.update_terrain_options()
            
            # 3. Sarlacc Pit setzen
            if hasattr(self, 'var_sarlacc_pit'):
                self.var_sarlacc_pit.set(data.get("sarlacc_pit", False))
            
            # 4. Punkte und Runden
            self.entry_punkte.delete(0, tk.END)
            self.entry_punkte.insert(0, str(data.get("points", "800")))
            
            self.entry_runden.delete(0, tk.END)
            self.entry_runden.insert(0, str(data.get("rounds", 6)))
            
            # 5. Deployment und Mission Type
            deployment = data.get("deployment", "")
            if deployment:
                try:
                    self.combo_deploy.set(deployment)
                except:
                    pass
            
            mission_type = data.get("mission_type", "")
            if mission_type:
                try:
                    self.combo_mission.set(mission_type)
                except:
                    pass
            
            # 6. Szenario-Text laden
            scenario_text = data.get("scenario_text", "") or data.get("prompt_text", "")
            self.current_scenario_text = scenario_text
            if hasattr(self, 'txt_output'):
                self.txt_output.delete("1.0", tk.END)
                if scenario_text:
                    self.txt_output.insert("1.0", scenario_text)
            
            # 7. AI-Settings
            ai_settings = data.get("ai_settings", {})
            if hasattr(self, 'var_gemini_enabled'):
                self.var_gemini_enabled.set(ai_settings.get("gemini_enabled", False))
            if hasattr(self, 'var_camera_upload'):
                self.var_camera_upload.set(ai_settings.get("camera_enabled", False))
            
            # 8. Musik-Settings
            music_settings = data.get("music", {})
            if hasattr(self, 'music_enabled_var'):
                self.music_enabled_var.set(music_settings.get("enabled", False))
            if hasattr(self, 'combo_playlist') and music_settings.get("playlist"):
                try:
                    self.combo_playlist.set(music_settings["playlist"])
                except:
                    pass
            
            # Karte aktualisieren
            self.update_map()
            
            logging.info("Mission loaded successfully.")
            messagebox.showinfo("Geladen", f"Mission geladen:\n{os.path.basename(file_path)}")
            
        except Exception as e:
            logging.error(f"Error loading mission: {e}", exc_info=True)
            messagebox.showerror("Fehler", f"Fehler beim Laden der Mission:\n{e}")

    def save_mission(self):
        logging.info("Attempting to save mission...")
        
        # Generate Map Image
        try:
            map_image_path = self.generate_map_image()
        except Exception as e:
            logging.error(f"Failed to generate map image: {e}")
            map_image_path = ""

        # Gather data
        data = {
            "deployment": self.combo_deploy.get(),
            "map_image": map_image_path,
            "mission_type": self.combo_mission.get(),
            "blue_faction": self.combo_blue.get(),
            "red_faction": self.combo_red.get(),
            "points": self.entry_punkte.get(),
            "rounds": int(self.entry_runden.get()) if self.entry_runden.get().isdigit() else 6,
            "terrain": [k for k,v in self.var_gelaende.items() if v.get()],
            "sarlacc_pit": self.var_sarlacc_pit.get() if hasattr(self, 'var_sarlacc_pit') else False,
            "prompt_text": self.txt_output.get("1.0", tk.END),
            "scenario_text": self.current_scenario_text,
            "ai_settings": {
                "gemini_enabled": self.var_gemini_enabled.get() if hasattr(self, 'var_gemini_enabled') else False,
                "camera_enabled": self.var_camera_upload.get() if hasattr(self, 'var_camera_upload') else False
            }
        }

        # Füge Musik-Einstellungen hinzu
        if hasattr(self, 'music_enabled_var') and self.music_enabled_var.get():
            data["music"] = {
                "enabled": True,
                "playlist": self.combo_playlist.get(),
                "volume": self.music_settings.get('volume', 70)
            }
            self.save_music_settings()

        if not data["blue_faction"] or not data["red_faction"]:
            logging.warning("Save failed: Factions not selected.")
            messagebox.showwarning("Fehler", "Bitte weise beiden Seiten eine Fraktion zu.")
            return

        initial_dir = get_writable_path("Missions")

        file_path = filedialog.asksaveasfilename(initialdir=initial_dir, title="Mission speichern", defaultextension=".json", filetypes=[("JSON", "*.json")])
        if file_path:
            try:
                logging.info(f"Saving mission to {file_path}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                logging.info("Mission saved successfully.")
                messagebox.showinfo("Gespeichert", f"Mission gespeichert in:\n{file_path}")
                
                # Musik-Einstellungen speichern (aber nicht starten)
                if data.get("music", {}).get("enabled"):
                    self.save_music_settings()
                    
            except Exception as e:
                logging.error(f"Error saving mission: {e}", exc_info=True)
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

    def update_map(self, event=None):
        self.current_deployment = self.combo_deploy.get()
        self.canvas.delete("all")

        w = self.canvas_width
        h = self.canvas_height

        # Draw Field (Blue)
        # Assuming 6x3. Scale: w=800 -> 6ft. h=400 -> 3ft.
        # Deployment zones depend on mode.

        # Background
        self.canvas.create_rectangle(0, 0, w, h, fill="#e1f5fe", outline="#0288d1", width=2)

        # Coordinates Helper
        def ft_to_px_w(ft): return (ft / 6.0) * w
        def ft_to_px_h(ft): return (ft / 3.0) * h

        # CHECK FOR CUSTOM DEPLOYMENT MAP
        custom_card = next((c for c in self.db.battle_cards if c["name"] == self.current_deployment and c.get("category") == "Deployment"), None)

        if custom_card and custom_card.get("map_file"):
            # Load custom map
            try:
                with open(custom_card["map_file"], "r") as f:
                    zones = json.load(f)

                # Scale factors (Creator was 600x300, Current is 800x400)
                # Ratio is same (2:1). Factor = 800/600 = 1.333
                scale_x = w / 600.0
                scale_y = h / 300.0

                for z in zones:
                    c = z["color"]
                    coords = z["coords"]

                    # Scale coords
                    x0 = coords[0] * scale_x
                    y0 = coords[1] * scale_y
                    x1 = coords[2] * scale_x
                    y1 = coords[3] * scale_y

                    fill = "#ffcdd2" if c == "red" else "#bbdefb"
                    outline = "red" if c == "red" else "blue"

                    self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline=outline)

            except Exception as e:
                self.canvas.create_text(w/2, h/2, text=f"Fehler beim Laden der Karte:\n{e}", fill="red")

            # Skip standard logic
        else:
            # Use standard deployment logic
            mode = self.current_deployment
            
            if mode == "Battle Lines":
                # Long edges, Range 1 deep.
                # Top edge (Red): 0 to Range 1 (0.5ft) height
                range_1_px = ft_to_px_h(0.5)

                # Red Zone (Top)
                self.canvas.create_rectangle(0, 0, w, range_1_px, fill="#ffcdd2", outline="red")
                self.canvas.create_text(w/2, range_1_px/2, text="ROT ZONE", fill="red", font=("bold"))

                # Blue Zone (Bottom)
                self.canvas.create_rectangle(0, h-range_1_px, w, h, fill="#bbdefb", outline="blue")
                self.canvas.create_text(w/2, h-(range_1_px/2), text="BLAU ZONE", fill="blue", font=("bold"))

            elif mode == "The Long March":
                # Short edges, Range 1 deep.
                # Left (Blue?), Right (Red?)
                range_1_px = ft_to_px_w(0.5)

                # Blue (Left)
                self.canvas.create_rectangle(0, 0, range_1_px, h, fill="#bbdefb", outline="blue")
                self.canvas.create_text(range_1_px/2, h/2, text="BLAU", fill="blue", font=("bold"), angle=90)

                # Red (Right)
                self.canvas.create_rectangle(w-range_1_px, 0, w, h, fill="#ffcdd2", outline="red")
                self.canvas.create_text(w-(range_1_px/2), h/2, text="ROT", fill="red", font=("bold"), angle=270)

            elif mode == "Major Offensive":
                # Corners.
                # Setup zones are L-shaped or triangles?
                # In Legion, Major Offensive is opposite corners.
                # Blue: Bottom Left. Red: Top Right.
                # Size: 4x2 area? No, typically Range 2 from corner.
                # Let's approx corner boxes.

                corner_w = ft_to_px_w(2.0) # Approx
                corner_h = ft_to_px_h(1.0)

                # Blue (Bottom Left)
                self.canvas.create_rectangle(0, h-corner_h, corner_w, h, fill="#bbdefb", outline="blue")
                self.canvas.create_text(corner_w/3, h-corner_h/2, text="BLAU", fill="blue")

                # Red (Top Right)
                self.canvas.create_rectangle(w-corner_w, 0, w, corner_h, fill="#ffcdd2", outline="red")
                self.canvas.create_text(w-corner_w/3, corner_h/2, text="ROT", fill="red")

            elif mode == "Disarray":
                # Corners, but split.
                # Blue: Top Left & Bottom Right.
                # Red: Top Right & Bottom Left.

                corner_w = ft_to_px_w(1.5)
                corner_h = ft_to_px_h(0.75)

                # Blue
                self.canvas.create_rectangle(0, 0, corner_w, corner_h, fill="#bbdefb", outline="blue")
                self.canvas.create_rectangle(w-corner_w, h-corner_h, w, h, fill="#bbdefb", outline="blue")

                # Red
                self.canvas.create_rectangle(w-corner_w, 0, w, corner_h, fill="#ffcdd2", outline="red")
                self.canvas.create_rectangle(0, h-corner_h, corner_w, h, fill="#ffcdd2", outline="red")

            elif mode == "Danger Close":
                # Center split? Or close lines?
                # Battle Lines but Range 2?
                # Let's assuming thicker strips.
                range_2_px = ft_to_px_h(1.0)

                self.canvas.create_rectangle(0, 0, w, range_2_px, fill="#ffcdd2", outline="red")
                self.canvas.create_rectangle(0, h-range_2_px, w, h, fill="#bbdefb", outline="blue")

            elif mode == "Hemmed In":
                # Center circle vs Edges?
                # Blue (Defender) center, Red (Attacker) edges?
                # Approx circle in middle

                # Center (Blue)
                cx, cy = w/2, h/2
                r = ft_to_px_h(0.75)
                self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#bbdefb", outline="blue")
                self.canvas.create_text(cx, cy, text="BLAU", fill="blue")

                # Edges (Red)
                # Surrounding? Or two sides?
                # Let's draw strips on Left/Right
                strip = ft_to_px_w(0.5)
                self.canvas.create_rectangle(0, 0, strip, h, fill="#ffcdd2", outline="red")
                self.canvas.create_rectangle(w-strip, 0, w, h, fill="#ffcdd2", outline="red")

            elif "Hinterhalt" in mode or "Ambush" in mode:
                # Defender Center (Blue), Attacker Surround (Red)
                # Center Box Range 1 away from edges?
                # Or Center Box Size?
                # Standard: Defender setup within Range 2 of center token?
                # Let's do: Center Box (Blue), Everything else (Red)? Or Edges?
                # Assume: Defender has a central zone. Attacker starts at edges.

                # Blue Center
                center_w = ft_to_px_w(2.0)
                center_h = ft_to_px_h(1.0)
                cx, cy = w/2, h/2

                self.canvas.create_rectangle(cx - center_w/2, cy - center_h/2, cx + center_w/2, cy + center_h/2, fill="#bbdefb", outline="blue")
                self.canvas.create_text(cx, cy, text="BLAU (Verteidiger)", fill="blue")

                # Red Edges (Strip)
                strip = ft_to_px_h(0.5)
                self.canvas.create_rectangle(0, 0, w, strip, fill="#ffcdd2", outline="red") # Top
                self.canvas.create_rectangle(0, h-strip, w, h, fill="#ffcdd2", outline="red") # Bottom
                self.canvas.create_rectangle(0, 0, strip, h, fill="#ffcdd2", outline="red") # Left
                self.canvas.create_rectangle(w-strip, 0, w, h, fill="#ffcdd2", outline="red") # Right

            elif "Einkesselung" in mode or "Encirclement" in mode:
                # Similar to Long March but Defender is pinched?
                # Blue Center Strip. Red Left AND Right.

                # Blue Center Strip
                strip_w = ft_to_px_w(2.0)
                cx = w/2
                self.canvas.create_rectangle(cx - strip_w/2, 0, cx + strip_w/2, h, fill="#bbdefb", outline="blue")
                self.canvas.create_text(cx, h/2, text="BLAU", fill="blue")

                # Red Sides
                side_w = ft_to_px_w(1.0)
                self.canvas.create_rectangle(0, 0, side_w, h, fill="#ffcdd2", outline="red")
                self.canvas.create_rectangle(w-side_w, 0, w, h, fill="#ffcdd2", outline="red")

            elif "Nahkampf" in mode or "Close Quarters" in mode:
                # Very close battle lines. Range 1 apart?
                # Middle of board.
                mid_h = h/2
                zone_h = ft_to_px_h(1.0)

                # Red Top (Ends at mid - 0.5)
                self.canvas.create_rectangle(0, 0, w, mid_h - (zone_h/2), fill="#ffcdd2", outline="red")

                # Blue Bottom (Starts at mid + 0.5)
                self.canvas.create_rectangle(0, mid_h + (zone_h/2), w, h, fill="#bbdefb", outline="blue")

                self.canvas.create_text(w/2, h/2, text="--- ENGAGEMENT ---", fill="#333")

        # Labels for Armies (Factions)
        blue_fac = self.combo_blue.get()
        red_fac = self.combo_red.get()

        if blue_fac:
            txt = f"BLAU: {blue_fac}"
            self.canvas.create_text(w/2, h-20, text=txt, font=("bold"), fill="#0d47a1")

        if red_fac:
            txt = f"ROT: {red_fac}"
            self.canvas.create_text(w/2, 20, text=txt, font=("bold"), fill="#b71c1c")

        # Draw Objectives
        mission = self.combo_mission.get()

        # Helper for Token
        def draw_token(x, y, label="?"):
            r = 15
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="#66bb6a", outline="green", width=2)
            self.canvas.create_text(x, y, text=label, font=("bold"))

        if "Abfangen" in mission or "Intercept" in mission or "Schlüssel" in mission or "Key" in mission:
            # 3 Points usually. Center, Left, Right?
            # Range 2 from Center? Or Range 4 from each other?
            # Center
            draw_token(w/2, h/2, "C")
            # Left/Right (approx)
            draw_token(w/4, h/2, "L")
            draw_token(3*w/4, h/2, "R")

        elif "Durchbruch" in mission or "Breakthrough" in mission:
            # Highlight Opponent Deployment Zones
            # We assume user knows rules (score in enemy zone).
            # Draw Arrows?
            self.canvas.create_line(w/2, h-50, w/2, 50, arrow=tk.LAST, width=5, fill="orange")
            self.canvas.create_text(w/2 + 20, h/2, text="ZIEL: Gegnerische Zone", fill="orange", angle=90)

        elif "Eliminierung" in mission or "Deathmatch" in mission:
            # Skull Icon or text
            self.canvas.create_text(w/2, h/2, text="☠ KILL ☠", font=("Arial", 30, "bold"), fill="red")

        elif "Evakuierung" in mission or "Hostage" in mission:
            # Hostage in deployment zone?
            # 1 Blue Hostage in Red Zone, 1 Red Hostage in Blue Zone?
            # Or Hostage starts with Player?
            # Usually Hostage Exchange: Unit carries it.
            # Draw Token in Deployment Zones
            draw_token(w/2, 40, "H (Rot)")
            draw_token(w/2, h-40, "H (Blau)")

        elif "Vorräte" in mission or "Recover" in mission:
            # Central Box (Range 1?) -> 5 Tokens usually
            # Center Token + 4 around it?
            cx, cy = w/2, h/2
            draw_token(cx, cy, "C")
            off = ft_to_px_w(1.0)
            draw_token(cx-off, cy, "1")
            draw_token(cx+off, cy, "2")
            draw_token(cx, cy-off, "3")
            draw_token(cx, cy+off, "4")

        elif "Sabotage" in mission:
            # Vaps: 2 for Blue, 2 for Red.
            # Blue Vaps in Blue Territory
            draw_token(w/4, h-50, "V")
            draw_token(3*w/4, h-50, "V")

            # Red Vaps
            draw_token(w/4, 50, "V")
            draw_token(3*w/4, 50, "V")

    def generate_prompt(self):
        # Daten sammeln
        fraktionen_gewaehlt = [k for k, v in self.var_fraktionen.items() if v.get()]
        terrain_gewaehlt = [k for k, v in self.var_gelaende.items() if v.get()]
        punkte = self.entry_punkte.get() if self.entry_punkte.get() else "800"

        deploy = self.combo_deploy.get()
        mission = self.combo_mission.get()

        if not fraktionen_gewaehlt:
            # Fallback if manual call
            return "Bitte Fraktionen wählen."
        
        str_fraktionen = ", ".join(fraktionen_gewaehlt)
        str_terrain = ", ".join(terrain_gewaehlt) if terrain_gewaehlt else "Zufällig / Keine Präferenz"
        
        # Sarlacc Pit Hinweis für Wüste
        sarlacc_hinweis = ""
        if hasattr(self, 'var_sarlacc_pit') and self.var_sarlacc_pit.get():
            sarlacc_hinweis = " **WICHTIG: Ein Sarlacc Pit ist auf dem Schlachtfeld vorhanden!** Erstelle spezielle Regeln für dieses gefährliche Terrain-Element."

        prompt = (
            f"Erstelle eine detaillierte und balancierte Mission für Star Wars: Legion.\n\n"
            f"**Rahmenbedingungen:**\n"
            f"- **Punkte:** {punkte} Punkte pro Seite.\n"
            f"- **Beteiligte Fraktionen:** {str_fraktionen}.\n"
            f"- **Gelände-Setting:** {str_terrain}.{sarlacc_hinweis}\n"
            f"- **Aufstellung:** {deploy}.\n"
            f"- **Mission/Objektive:** {mission}.\n\n"
            f"**Anforderungen an die Mission:**\n"
            f"1. **Narrativer Hintergrund:** Erstelle eine Story, die genau erklärt, warum diese Fraktionen in diesem spezifischen Gelände ({str_terrain}) kämpfen.\n"
            f"2. **Schlachtfeld:** Beschreibe den Aufbau passend zur Aufstellung '{deploy}'. Welche spezifischen Geländestücke werden benötigt?\n"
            f"3. **Ziele:** Beschreibe die Mechanik für die Mission '{mission}'. Wie punkten die Spieler?\n"
            f"4. **Sonderregeln:** Erfinde 1-2 Umwelt-Regeln, die typisch für dieses Gelände sind.\n"
            f"5. **Siegbedingungen:** Nenne die Bedingungen für den Sieg.\n\n"
            f"Antworte auf Deutsch und formatiere die Antwort übersichtlich."
        )
        return prompt

    def generate_scenario_with_gemini(self):
        if not GEMINI_AVAILABLE and not REQUESTS_AVAILABLE:
            messagebox.showerror("Fehler", "Weder google-genai noch requests sind verfügbar.")
            return

        if not self.api_key:
            messagebox.showerror("Fehler", "Kein API Key gefunden (gemini_key.txt fehlt).")
            return

        prompt = self.generate_prompt()
        if "Bitte Fraktionen wählen" in prompt:
            messagebox.showwarning("Fehler", "Wähle mindestens eine Fraktion!")
            return

        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, "Generiere Szenario mit Gemini AI... Bitte warten...\n")
        self.root.update()

        try:
            text_content = ""
            if GEMINI_VERSION == 2:
                # Use new SDK
                client = genai.Client(api_key=self.api_key)
                models_to_try = ['gemini-3-flash-preview', 'gemini-3-pro-preview', 'gemini-2.5-flash', 'gemini-2.0-flash']
                response = None
                last_err = None

                for model_name in models_to_try:
                    try:
                        logging.info(f"Gemini (v2): Trying model {model_name}")
                        response = client.models.generate_content(
                            model=model_name,
                            contents=[prompt]
                        )
                        if response:
                            logging.info(f"Gemini (v2): Success with {model_name}")
                            text_content = response.text
                            break
                    except Exception as e:
                        logging.warning(f"Gemini (v2): Failed with {model_name}: {e}")
                        last_err = e
                
                if not text_content:
                    if last_err:
                        raise last_err
                    else:
                        raise Exception("No response from Gemini (v2)")
                
            elif GEMINI_VERSION == 1:
                # Use old SDK - Try to use 2.0 or just 1.5 if that's all V1 supports, but 1.5 is 404ing.
                # Attempt to use newer names with V1 if possible
                genai.configure(api_key=self.api_key)
                
                # List of potential models for V1
                v1_models = ['gemini-2.0-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-pro']
                model = None
                
                for m_name in v1_models:
                    try:
                        logging.info(f"Gemini (v1): Trying model {m_name}")
                        model = genai.GenerativeModel(m_name)
                        response = model.generate_content(prompt)
                        text_content = response.text
                        logging.info(f"Gemini (v1): Success with {m_name}")
                        break
                    except Exception as e:
                         logging.warning(f"Gemini (v1): Failed with {m_name}: {e}")

                if not text_content:
                     # Fallback to the original one just in case
                     model = genai.GenerativeModel('gemini-1.5-flash')
                     response = model.generate_content(prompt)
                     text_content = response.text
                
            elif REQUESTS_AVAILABLE:
                # Fallback to REST API - Try multiple models
                # Validated models from API listing (Feb 2026)
                models = ["gemini-3-flash-preview", "gemini-3-pro-preview", "gemini-2.5-flash", "gemini-2.0-flash"]
                success = False
                
                logging.info(f"MissionBuilder: Starting REST API fallback with models: {models}")
                
                for m in models:
                    # Construct URL - handle whether model string already contains 'models/' or not
                    if m.startswith("models/"):
                        model_path = m
                    else:
                        model_path = f"models/{m}"
                        
                    url = f"https://generativelanguage.googleapis.com/v1beta/{model_path}:generateContent?key={self.api_key}"
                    headers = {'Content-Type': 'application/json'}
                    data = {
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }]
                    }
                    try:
                        msg = f"\nVersuche Modell: {m}..."
                        self.txt_output.insert(tk.END, msg)
                        print(f"DEBUG: {msg.strip()}")
                        logging.info(f"MissionBuilder: Trying model {m}")
                        
                        self.root.update()
                        response = requests.post(url, headers=headers, json=data)
                        
                        if response.status_code == 200:
                            result = response.json()
                            text_content = result['candidates'][0]['content']['parts'][0]['text']
                            success = True
                            logging.info(f"MissionBuilder: Success with model {m}")
                            print(f"DEBUG: Success with model {m}")
                            break
                        else:
                            warn_msg = f"Model {m} failed: {response.status_code} - {response.text}"
                            logging.warning(warn_msg)
                            print(f"DEBUG: {warn_msg}")
                    except Exception as e:
                        logging.error(f"MissionBuilder: Exception for {m}: {e}")
                        print(f"DEBUG: Exception for {m}: {e}")
                        continue
                        
                if not success:
                     err_msg = f"\nAlle Modelle fehlgeschlagen. Letzter Status: {response.status_code if 'response' in locals() else 'Unknown'}"
                     self.txt_output.insert(tk.END, err_msg)
                     logging.error(f"MissionBuilder: All fallback models failed.")
                     return

            # Display Result
            self.current_scenario_text = text_content
            self.txt_output.delete("1.0", tk.END)
            self.insert_formatted_text(self.txt_output, text_content)

        except Exception as e:
            self.txt_output.insert(tk.END, f"\nFehler bei Gemini Anfrage: {e}")

    def create_music_section(self, parent):
        """Erstellt die Musik-Einstellungen Sektion"""
        lbl_musik = tk.Label(parent, text="🎵 Musik Einstellungen:", font=("Arial", 11, "bold"))
        lbl_musik.pack(anchor="w", pady=(15, 5))

        frame_musik = tk.Frame(parent, relief=tk.GROOVE, borderwidth=1)
        frame_musik.pack(fill="x", pady=5, padx=2)

        # Musik An/Aus Checkbox
        self.music_enabled_var = tk.BooleanVar(value=self.music_settings.get('enabled', False))
        chk_music = tk.Checkbutton(frame_musik, text="Mission mit Musik abspielen", 
                                  variable=self.music_enabled_var,
                                  command=self.on_music_enabled_change)
        chk_music.pack(anchor="w", padx=5, pady=5)

        # Playlist Frame (nur sichtbar wenn Musik aktiviert)
        self.playlist_frame = tk.Frame(frame_musik)
        if self.music_enabled_var.get():
            self.playlist_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(self.playlist_frame, text="Playlist auswählen:").pack(anchor="w")
        
        # Playlist Combobox
        self.combo_playlist = ttk.Combobox(self.playlist_frame, state="readonly", width=40)
        self.combo_playlist.pack(fill="x", pady=2)
        
        # Playlist Buttons
        btn_frame_playlist = tk.Frame(self.playlist_frame)
        btn_frame_playlist.pack(fill="x", pady=5)
        
        tk.Button(btn_frame_playlist, text="🔄 Playlists aktualisieren", 
                 command=self.refresh_playlists, bg="#FF9800", fg="white").pack(side="left", padx=2)
        tk.Button(btn_frame_playlist, text="➕ Neue Playlist", 
                 command=self.create_new_playlist, bg="#4CAF50", fg="white").pack(side="left", padx=2)

    def create_ai_section(self, parent):
        """Erstellt die AI & Gemini Einstellungen"""
        lbl_ai = tk.Label(parent, text="🤖 AI & Gemini Integration:", font=("Arial", 11, "bold"))
        lbl_ai.pack(anchor="w", pady=(15, 5))

        frame_ai = tk.Frame(parent, relief=tk.GROOVE, borderwidth=1)
        frame_ai.pack(fill="x", pady=5, padx=2)

        # Gemini Enable
        self.var_gemini_enabled = tk.BooleanVar(value=True)
        chk_gemini = tk.Checkbutton(frame_ai, text="Gemini AI zur Entscheidungshilfe nutzen", variable=self.var_gemini_enabled)
        chk_gemini.pack(anchor="w", padx=5)

        # Camera Upload Enable
        self.var_camera_upload = tk.BooleanVar(value=True)
        chk_cam = tk.Checkbutton(frame_ai, text="📸 Foto-Upload bei Entscheidungen (Webcam)", variable=self.var_camera_upload)
        chk_cam.pack(anchor="w", padx=5, pady=2)
        
        tk.Label(frame_ai, text="ℹ️ Fotos werden zur Situationsanalyse an Gemini gesendet.", font=("Arial", 8), fg="gray").pack(anchor="w", padx=20)

    def on_music_enabled_change(self):
        """Wird aufgerufen wenn Musik aktiviert/deaktiviert wird"""
        if self.music_enabled_var.get():
            self.playlist_frame.pack(fill="x", padx=5, pady=5)
        else:
            self.playlist_frame.pack_forget()
        self.save_music_settings()

    def refresh_playlists(self):
        """Lädt verfügbare Playlists neu"""
        try:
            # Bestimme Playlist-Verzeichnis
            if getattr(sys, 'frozen', False):
                # EXE Modus
                exe_dir = os.path.dirname(sys.executable)
                playlist_dir = os.path.join(exe_dir, "playlist")
            else:
                # Script Modus
                project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                playlist_dir = os.path.join(project_dir, "playlist")
            
            if not os.path.exists(playlist_dir):
                self.combo_playlist['values'] = ["Keine Playlists gefunden"]
                return
                
            # Lade Playlist-Namen
            playlists = []
            for file_name in os.listdir(playlist_dir):
                if file_name.endswith('.json'):
                    try:
                        playlist_path = os.path.join(playlist_dir, file_name)
                        with open(playlist_path, 'r', encoding='utf-8') as f:
                            playlist_data = json.load(f)
                            playlist_name = playlist_data.get('name', file_name[:-5])
                            playlists.append(playlist_name)
                    except:
                        continue
            
            self.combo_playlist['values'] = playlists if playlists else ["Keine Playlists gefunden"]
            
        except Exception as e:
            self.combo_playlist['values'] = ["Fehler beim Laden der Playlists"]

    def create_new_playlist(self):
        """Öffnet Dialog zum Erstellen einer neuen Playlist"""
        try:
            from utilities.MusicPlayer import MusicPlayer
            new_window = tk.Toplevel(self.root)
            new_window.withdraw()
            music_player = MusicPlayer(new_window)
            new_window.deiconify()
            music_player.create_new_playlist()
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Musikplayer nicht öffnen: {e}")

    def open_music_player(self):
        """Öffnet den Musikplayer"""
        try:
            from utilities.MusicPlayer import MusicPlayer
            new_window = tk.Toplevel(self.root)
            new_window.withdraw()
            music_player = MusicPlayer(new_window)
            new_window.deiconify()
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Musikplayer nicht öffnen: {e}")

    def load_music_settings(self):
        """Lädt gespeicherte Musik-Einstellungen"""
        try:
            settings_dir = get_writable_path("settings")
            settings_file = os.path.join(settings_dir, "mission_music_settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {
            'enabled': False,
            'last_playlist': None,
            'volume': 70,
            'current_song': None
        }

    def save_music_settings(self):
        """Speichert Musik-Einstellungen"""
        try:
            settings = {
                'enabled': self.music_enabled_var.get(),
                'last_playlist': self.combo_playlist.get() if hasattr(self, 'combo_playlist') else None,
                'volume': self.music_settings.get('volume', 70),
                'current_song': self.music_settings.get('current_song')
            }
            
            settings_dir = get_writable_path("settings")
            settings_file = os.path.join(settings_dir, "mission_music_settings.json")
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            self.music_settings = settings
        except Exception as e:
            print(f"Fehler beim Speichern der Musik-Einstellungen: {e}")

    def start_mission_with_music(self, mission_data):
        """Startet Mission mit Musik falls aktiviert"""
        if not self.music_enabled_var.get():
            return
            
        selected_playlist = self.combo_playlist.get()
        if not selected_playlist or selected_playlist == "Keine Playlists gefunden":
            return
            
        try:
            # Speichere Mission mit Musik-Info
            mission_data['music'] = {
                'enabled': True,
                'playlist': selected_playlist,
                'volume': self.music_settings.get('volume', 70)
            }
            
            # Öffne Musikplayer mit der Playlist
            self.launch_music_player_with_playlist(selected_playlist)
            
        except Exception as e:
            print(f"Fehler beim Starten der Mission mit Musik: {e}")

    def launch_music_player_with_playlist(self, playlist_name):
        """Startet den Musikplayer mit einer bestimmten Playlist"""
        try:
            from utilities.MusicPlayer import MusicPlayer
            import threading
            
            def start_music():
                new_window = tk.Toplevel(self.root)
                new_window.withdraw()
                music_player = MusicPlayer(new_window)
                
                # Lade und spiele die Playlist
                if playlist_name in music_player.playlists:
                    playlist_data = music_player.playlists[playlist_name]
                    music_player.current_playlist = playlist_data.get('tracks', [])
                    if music_player.current_playlist:
                        music_player.current_track_index = 0
                        music_player.play_current_track()
                
                new_window.deiconify()
            
            # Starte in separatem Thread um UI nicht zu blockieren
            threading.Thread(target=start_music, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Musikplayer nicht starten: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LegionMissionGenerator(root)
    root.mainloop()