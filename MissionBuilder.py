import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import random
import os

class LegionMissionGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("SW Legion: Mission & Map Generator")
        self.root.geometry("1400x900")
        
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
            chk = tk.Checkbutton(frame_fraktionen, text=frak, variable=var, anchor="w")
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
            text="PROMPT ERSTELLEN & KOPIEREN", 
            command=self.generate_prompt,
            bg="#2196F3", fg="white", font=("Arial", 12, "bold"), height=2
        )
        btn_gen.pack(pady=20, fill="x")

        # 5. VORSCHAU
        lbl_output = tk.Label(frame_settings, text="Vorschau:", font=("Arial", 9))
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
            "Battle Lines", "The Long March", "Disarray", "Major Offensive", "Danger Close", "Hemmed In"
        ], state="readonly")
        self.combo_deploy.current(0)
        self.combo_deploy.pack(side="left", padx=5)
        self.combo_deploy.bind("<<ComboboxSelected>>", self.update_map)

        tk.Button(frame_deploy_ctrl, text="Zufällig", command=self.random_deploy, bg="#FF9800", fg="white").pack(side="left", padx=5)

        # Army Loader Buttons
        frame_armies = tk.Frame(frame_map, bg="#eee")
        frame_armies.pack(fill="x", pady=10)

        self.btn_load_blue = tk.Button(frame_armies, text="Lade Armee BLAU (Unten)", command=lambda: self.load_army("Blue"), bg="#2196F3", fg="white", width=25)
        self.btn_load_blue.pack(side="left", padx=10)

        self.btn_load_red = tk.Button(frame_armies, text="Lade Armee ROT (Oben)", command=lambda: self.load_army("Red"), bg="#F44336", fg="white", width=25)
        self.btn_load_red.pack(side="right", padx=10)

        # Draw Initial
        self.update_map()

    def random_deploy(self):
        opts = ["Battle Lines", "The Long March", "Disarray", "Major Offensive", "Danger Close", "Hemmed In"]
        self.combo_deploy.set(random.choice(opts))
        self.update_map()

    def load_army(self, side):
        initial_dir = "Armeen"
        if not os.path.exists(initial_dir): os.makedirs(initial_dir)

        file_path = filedialog.askopenfilename(initialdir=initial_dir, title=f"Armee {side} laden", filetypes=[("JSON", "*.json")])
        if not file_path: return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            faction = data.get("faction", "Unknown")
            # Extract name from filename or first unit?
            name = os.path.basename(file_path).replace(".json", "")

            army_data = {"faction": faction, "name": name}

            if side == "Blue":
                self.blue_army = army_data
                self.btn_load_blue.config(text=f"BLAU: {faction}")
            else:
                self.red_army = army_data
                self.btn_load_red.config(text=f"ROT: {faction}")

            self.update_map()

        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Datei nicht laden: {e}")

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

        # Labels for Armies
        if self.blue_army:
            txt = f"{self.blue_army['faction']}\n({self.blue_army['name']})"
            # Place in Blue zone (approx Bottom Center usually)
            self.canvas.create_text(w/2, h-20, text=txt, font=("bold"), fill="#0d47a1")

        if self.red_army:
            txt = f"{self.red_army['faction']}\n({self.red_army['name']})"
            # Place in Red zone (approx Top Center usually)
            self.canvas.create_text(w/2, 20, text=txt, font=("bold"), fill="#b71c1c")

    def generate_prompt(self):
        # Daten sammeln
        fraktionen_gewaehlt = [k for k, v in self.var_fraktionen.items() if v.get()]
        terrain_gewaehlt = [k for k, v in self.var_gelaende.items() if v.get()]
        punkte = self.entry_punkte.get() if self.entry_punkte.get() else "800"

        # Validierung
        if not fraktionen_gewaehlt:
            messagebox.showwarning("Fehler", "Wähle mindestens eine Fraktion!")
            return
        
        # Textbausteine
        str_fraktionen = ", ".join(fraktionen_gewaehlt)
        str_terrain = ", ".join(terrain_gewaehlt) if terrain_gewaehlt else "Zufällig / Keine Präferenz"

        # Prompt zusammenbauen
        prompt = (
            f"Erstelle eine detaillierte und balancierte Mission für Star Wars: Legion.\n\n"
            f"**Rahmenbedingungen:**\n"
            f"- **Punkte:** {punkte} Punkte pro Seite.\n"
            f"- **Beteiligte Fraktionen:** {str_fraktionen}.\n"
            f"- **Gelände-Setting:** {str_terrain}.\n\n"
            f"**Anforderungen an die Mission:**\n"
            f"1. **Narrativer Hintergrund:** Erstelle eine Story, die genau erklärt, warum diese Fraktionen in diesem spezifischen Gelände ({str_terrain}) kämpfen.\n"
            f"2. **Schlachtfeld:** Beschreibe den Aufbau. Welche spezifischen Geländestücke (passend zum gewählten Setting) werden benötigt und wie beeinflussen sie Sichtlinien und Deckung?\n"
            f"3. **Ziele:** Definiere Primär- und Sekundärziele.\n"
            f"4. **Sonderregeln:** Erfinde 1-2 Umwelt-Regeln, die typisch für dieses Gelände sind (z.B. Sandsturm bei Wüste, Kälte bei Schnee, enge Gassen bei Stadt).\n"
            f"5. **Siegbedingungen:** Nenne die Bedingungen für den Sieg.\n\n"
            f"Antworte auf Deutsch und formatiere die Antwort übersichtlich."
        )

        # Ausgabe
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, prompt)
        
        self.root.clipboard_clear()
        self.root.clipboard_append(prompt)
        
        messagebox.showinfo("Kopiert", "Der Prompt wurde in die Zwischenablage kopiert!")

if __name__ == "__main__":
    root = tk.Tk()
    app = LegionMissionGenerator(root)
    root.mainloop()