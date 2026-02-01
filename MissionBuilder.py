import tkinter as tk
from tkinter import messagebox

class LegionMissionGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("SW Legion: Mission & Map Generator")
        self.root.geometry("600x750")  # Fenster etwas größer gemacht
        
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
        
        # GUI Elemente erstellen
        self.create_widgets()

    def create_widgets(self):
        # --- Haupt-Container (Canvas für Scrollen wäre besser, aber wir packen es einfach) ---
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. FRAKTIONEN
        lbl_frake = tk.Label(main_frame, text="1. Beteiligte Armeen:", font=("Arial", 11, "bold"))
        lbl_frake.pack(anchor="w", pady=(0, 5))

        frame_fraktionen = tk.Frame(main_frame, relief=tk.GROOVE, borderwidth=1)
        frame_fraktionen.pack(fill="x", pady=5)

        for frak in self.fraktionen:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(frame_fraktionen, text=frak, variable=var, anchor="w")
            chk.pack(fill="x", padx=5)
            self.var_fraktionen[frak] = var

        # 2. GELÄNDE / TERRAIN
        lbl_terrain = tk.Label(main_frame, text="2. Gelände & Umgebung:", font=("Arial", 11, "bold"))
        lbl_terrain.pack(anchor="w", pady=(15, 5))

        frame_terrain = tk.Frame(main_frame, relief=tk.GROOVE, borderwidth=1)
        frame_terrain.pack(fill="x", pady=5)

        for gelaende in self.gelaende_typen:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(frame_terrain, text=gelaende, variable=var, anchor="w")
            chk.pack(fill="x", padx=5)
            self.var_gelaende[gelaende] = var

        # 3. PUNKTE
        lbl_punkte = tk.Label(main_frame, text="3. Punktezahl:", font=("Arial", 11, "bold"))
        lbl_punkte.pack(anchor="w", pady=(15, 5))

        self.entry_punkte = tk.Entry(main_frame, font=("Arial", 10))
        self.entry_punkte.insert(0, "800")
        self.entry_punkte.pack(fill="x", pady=5)

        # 4. BUTTON
        btn_gen = tk.Button(
            main_frame, 
            text="PROMPT ERSTELLEN & KOPIEREN", 
            command=self.generate_prompt,
            bg="#2196F3", fg="white", font=("Arial", 12, "bold"), height=2
        )
        btn_gen.pack(pady=20, fill="x")

        # 5. VORSCHAU
        lbl_output = tk.Label(main_frame, text="Vorschau:", font=("Arial", 9))
        lbl_output.pack(anchor="w")

        self.txt_output = tk.Text(main_frame, height=8, font=("Consolas", 8), wrap="word")
        self.txt_output.pack(fill="both", expand=True)

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