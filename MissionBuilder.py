import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import random
import os
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class LegionMissionGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("SW Legion: Mission & Map Generator")
        self.root.geometry("1400x900")

        self.api_key = self.load_api_key()
        self.current_scenario_text = ""
        
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
            chk = tk.Checkbutton(frame_terrain, text=gelaende, variable=var, anchor="w")
            chk.pack(fill="x", padx=5)
            self.var_gelaende[gelaende] = var

        # 3. PUNKTE
        lbl_punkte = tk.Label(frame_settings, text="3. Punktezahl:", font=("Arial", 11, "bold"))
        lbl_punkte.pack(anchor="w", pady=(15, 5))

        self.entry_punkte = tk.Entry(frame_settings, font=("Arial", 10))
        self.entry_punkte.insert(0, "800")
        self.entry_punkte.pack(fill="x", pady=5)

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

        tk.Label(frame_deploy_ctrl, text="Aufstellung:", bg="#eee").pack(side="left")
        self.combo_deploy = ttk.Combobox(frame_deploy_ctrl, values=[
            "Battle Lines", "The Long March", "Disarray", "Major Offensive", "Danger Close", "Hemmed In",
            "Hinterhalt (Ambush)", "Einkesselung (Encirclement)", "Nahkampf (Close Quarters)"
        ], state="readonly")
        self.combo_deploy.current(0)
        self.combo_deploy.pack(side="left", padx=5)
        self.combo_deploy.bind("<<ComboboxSelected>>", self.update_map)

        # Mission / Objective Control
        tk.Label(frame_deploy_ctrl, text="Mission:", bg="#eee").pack(side="left", padx=(10,0))
        self.combo_mission = ttk.Combobox(frame_deploy_ctrl, values=[
            "Kein Marker",
            "Abfangen (Intercept)",
            "Schlüsselpositionen (Key Positions)",
            "Durchbruch (Breakthrough)",
            "Eliminierung (Deathmatch)",
            "Evakuierung (Hostage)",
            "Vorräte bergen (Recover Supplies)",
            "Sabotage"
        ], state="readonly")
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

        # Save Mission
        tk.Button(frame_map, text="💾 Mission Speichern (für Game Companion)", command=self.save_mission, bg="#4CAF50", fg="white", font=("bold", 12)).pack(pady=20)

        # Draw Initial
        self.update_map()

    def random_deploy(self):
        opts_dep = ["Battle Lines", "The Long March", "Disarray", "Major Offensive", "Danger Close", "Hemmed In", "Hinterhalt (Ambush)", "Einkesselung (Encirclement)", "Nahkampf (Close Quarters)"]
        self.combo_deploy.set(random.choice(opts_dep))

        opts_mis = ["Abfangen (Intercept)", "Schlüsselpositionen (Key Positions)", "Durchbruch (Breakthrough)", "Eliminierung (Deathmatch)", "Evakuierung (Hostage)", "Vorräte bergen (Recover Supplies)", "Sabotage"]
        self.combo_mission.set(random.choice(opts_mis))

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

    def load_api_key(self):
        # Try to load from file
        try:
            if os.path.exists("gemini_key.txt"):
                with open("gemini_key.txt", "r") as f:
                    return f.read().strip()
        except:
            pass
        return ""

    def save_mission(self):
        # Gather data
        data = {
            "deployment": self.combo_deploy.get(),
            "mission_type": self.combo_mission.get(),
            "blue_faction": self.combo_blue.get(),
            "red_faction": self.combo_red.get(),
            "points": self.entry_punkte.get(),
            "terrain": [k for k,v in self.var_gelaende.items() if v.get()],
            "prompt_text": self.txt_output.get("1.0", tk.END),
            "scenario_text": self.current_scenario_text
        }

        if not data["blue_faction"] or not data["red_faction"]:
            messagebox.showwarning("Fehler", "Bitte weise beiden Seiten eine Fraktion zu.")
            return

        initial_dir = "Missions"
        if not os.path.exists(initial_dir): os.makedirs(initial_dir)

        file_path = filedialog.asksaveasfilename(initialdir=initial_dir, title="Mission speichern", defaultextension=".json", filetypes=[("JSON", "*.json")])
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Gespeichert", f"Mission gespeichert in:\n{file_path}")
            except Exception as e:
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

        # Draw Zones (Red)
        zones = [] # List of tuples (x1, y1, x2, y2, color_fill, text_tag)

        # Standard: Blue starts Bottom, Red starts Top (usually).
        # We will assume:
        # Blue = Player 1 (Bottom/Left)
        # Red = Player 2 (Top/Right)

        mode = self.current_deployment

        # Note: Legion standard is 6x3.
        # Range 1 = 6 inches = 0.5 ft.

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

        prompt = (
            f"Erstelle eine detaillierte und balancierte Mission für Star Wars: Legion.\n\n"
            f"**Rahmenbedingungen:**\n"
            f"- **Punkte:** {punkte} Punkte pro Seite.\n"
            f"- **Beteiligte Fraktionen:** {str_fraktionen}.\n"
            f"- **Gelände-Setting:** {str_terrain}.\n"
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
        if not REQUESTS_AVAILABLE:
            messagebox.showerror("Fehler", "Das Modul 'requests' fehlt. AI-Generierung nicht möglich.")
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

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                try:
                    text_content = result['candidates'][0]['content']['parts'][0]['text']
                    self.current_scenario_text = text_content
                    self.txt_output.delete("1.0", tk.END)
                    self.txt_output.insert(tk.END, text_content)
                except KeyError:
                    self.txt_output.insert(tk.END, f"\nFehler beim Parsen der Antwort: {result}")
            else:
                self.txt_output.insert(tk.END, f"\nAPI Fehler ({response.status_code}): {response.text}")
        except Exception as e:
            self.txt_output.insert(tk.END, f"\nVerbindungsfehler: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LegionMissionGenerator(root)
    root.mainloop()