import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

# =============================================================================
# TEIL 1: DIE DATENBANK (LOGIK & DATEN)
# =============================================================================

class LegionDatabase:
    def __init__(self):
        # ---------------------------------------------------------------------
        # 1. UPGRADE-LISTE
        # "restricted_to": None = Für alle. 
        # "restricted_to": ["Name"] = Nur für bestimmte Einheiten/Fraktionen.
        # ---------------------------------------------------------------------
        self.upgrades = [
            # --- MACHT (FORCE) ---
            {"name": "Machtschub (Force Push)", "type": "Force", "points": 10, "restricted_to": None},
            {"name": "Machtreflexe", "type": "Force", "points": 5, "restricted_to": None},
            {"name": "Säbelwurf", "type": "Force", "points": 5, "restricted_to": None},
            {"name": "Machtwürgen", "type": "Force", "points": 5, "restricted_to": ["Dunkle Seite", "Galaktisches Imperium", "Separatistenallianz"]},
            {"name": "Jedi-Gedankentrick", "type": "Force", "points": 5, "restricted_to": ["Helle Seite", "Rebellenallianz", "Galaktische Republik"]},
            
            # --- KOMMANDO (COMMAND) ---
            {"name": "Aggressive Taktiken", "type": "Command", "points": 15, "restricted_to": None},
            {"name": "Führungsqualitäten", "type": "Command", "points": 5, "restricted_to": None},
            {"name": "Strenge Befehle", "type": "Command", "points": 5, "restricted_to": None},
            {"name": "Improvisierte Befehle", "type": "Command", "points": 5, "restricted_to": None},

            # --- AUSRÜSTUNG (GEAR) ---
            {"name": "Zielausrüstung (Targeting Scopes)", "type": "Gear", "points": 4, "restricted_to": None},
            {"name": "Kletterhaken", "type": "Gear", "points": 1, "restricted_to": None},
            {"name": "Aufklärungsdaten (Recon Intel)", "type": "Gear", "points": 2, "restricted_to": None},
            {"name": "Stim-Packs", "type": "Gear", "points": 8, "restricted_to": None},
            {"name": "Notfall-Stims", "type": "Gear", "points": 8, "restricted_to": None},

            # --- TRAINING ---
            {"name": "Zähigkeit (Tenacity)", "type": "Training", "points": 4, "restricted_to": None},
            {"name": "Jäger (Hunter)", "type": "Training", "points": 6, "restricted_to": None},
            {"name": "Entschlossenheit (Duck and Cover)", "type": "Training", "points": 2, "restricted_to": None},
            {"name": "Überblick (Situational Awareness)", "type": "Training", "points": 2, "restricted_to": None},

            # --- KOMMUNIKATION (COMMS) ---
            {"name": "HQ-Uplink", "type": "Comms", "points": 10, "restricted_to": None},
            {"name": "Langstrecken-Comlink", "type": "Comms", "points": 5, "restricted_to": None},
            {"name": "Komms-Störsender", "type": "Comms", "points": 5, "restricted_to": None},

            # --- GRANATEN (GRENADES) ---
            {"name": "Erschütterungsgranaten", "type": "Grenades", "points": 3, "restricted_to": None},
            {"name": "Fragmentgranaten", "type": "Grenades", "points": 5, "restricted_to": None},
            {"name": "Impact-Granaten", "type": "Grenades", "points": 3, "restricted_to": None},

            # --- SCHWERE WAFFEN (IMPERIUM) ---
            {"name": "DLT-19 Stormtrooper", "type": "Heavy Weapon", "points": 20, "restricted_to": ["Stormtroopers"]},
            {"name": "HH-12 Stormtrooper", "type": "Heavy Weapon", "points": 16, "restricted_to": ["Stormtroopers"]},
            {"name": "T-21B Shoretrooper", "type": "Heavy Weapon", "points": 32, "restricted_to": ["Shoretroopers"]},
            {"name": "RT-97C (Snowtrooper)", "type": "Heavy Weapon", "points": 24, "restricted_to": ["Snowtroopers"]},
            {"name": "DLT-19D (Death Trooper)", "type": "Heavy Weapon", "points": 34, "restricted_to": ["Imperial Death Troopers"]},

            # --- SCHWERE WAFFEN (REBELLEN) ---
            {"name": "Z-6 Trooper", "type": "Heavy Weapon", "points": 20, "restricted_to": ["Rebel Troopers"]},
            {"name": "MPL-57 Ion Trooper", "type": "Heavy Weapon", "points": 18, "restricted_to": ["Rebel Troopers"]},
            {"name": "CM-O/93 (Veterans)", "type": "Heavy Weapon", "points": 26, "restricted_to": ["Rebel Veterans"]},
            {"name": "Sniper (Commandos)", "type": "Heavy Weapon", "points": 28, "restricted_to": ["Rebel Commandos"]},

            # --- SCHWERE WAFFEN (SEPARATISTEN) ---
            {"name": "E-5C B1 Trooper", "type": "Heavy Weapon", "points": 16, "restricted_to": ["B1 Battle Droids"]},
            {"name": "E-60R B1 Trooper", "type": "Heavy Weapon", "points": 18, "restricted_to": ["B1 Battle Droids"]},
            {"name": "ACM B2 Trooper", "type": "Heavy Weapon", "points": 24, "restricted_to": ["B2 Super Battle Droids"]},
            {"name": "B2-HA Trooper", "type": "Heavy Weapon", "points": 30, "restricted_to": ["B2 Super Battle Droids"]},

            # --- SCHWERE WAFFEN (REPUBLIK) ---
            {"name": "Z-6 Phase I Clone", "type": "Heavy Weapon", "points": 23, "restricted_to": ["Phase I Clone Troopers"]},
            {"name": "DC-15 Phase I Clone", "type": "Heavy Weapon", "points": 26, "restricted_to": ["Phase I Clone Troopers"]},
            {"name": "RPS-6 Phase I Clone", "type": "Heavy Weapon", "points": 21, "restricted_to": ["Phase I Clone Troopers"]},
            {"name": "Z-6 Phase II Clone", "type": "Heavy Weapon", "points": 27, "restricted_to": ["Phase II Clone Troopers"]},
            {"name": "Mortar Trooper", "type": "Heavy Weapon", "points": 18, "restricted_to": ["Phase II Clone Troopers"]},

            # --- PILOTEN ---
            {"name": "Imperialer Hammer-Pilot", "type": "Pilot", "points": 10, "restricted_to": ["Galaktisches Imperium"]},
            {"name": "Wedge Antilles", "type": "Pilot", "points": 5, "restricted_to": ["Rebellenallianz"]},
            {"name": "Ryder Azadi", "type": "Pilot", "points": 5, "restricted_to": ["Rebellenallianz"]},
        ]

        # ---------------------------------------------------------------------
        # 2. EINHEITEN-LISTE
        # ---------------------------------------------------------------------
        self.units = {
            "Galaktisches Imperium": [
                {"name": "Darth Vader (Commander)", "points": 190, "rank": "Commander", "hp": 8, "courage": "-", "slots": ["Force", "Force", "Command"], "info": "Deflect, Immune: Pierce"},
                {"name": "Imperator Palpatine", "points": 190, "rank": "Commander", "hp": 5, "courage": "-", "slots": ["Force", "Force", "Force", "Command"], "info": "Pulling the Strings"},
                {"name": "General Veers", "points": 75, "rank": "Commander", "hp": 5, "courage": 2, "slots": ["Command", "Gear"], "info": "Spotter 2, Inspire 1"},
                {"name": "Iden Versio", "points": 100, "rank": "Commander", "hp": 6, "courage": 3, "slots": ["Training", "Gear", "Armament", "Comms"], "info": "Loadout, Marksman, Nimble"},
                {"name": "Stormtroopers", "points": 44, "rank": "Corps", "hp": 1, "courage": 1, "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Precise 1"},
                {"name": "Shoretroopers", "points": 52, "rank": "Corps", "hp": 1, "courage": 1, "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Target 1, Coordinate"},
                {"name": "Snowtroopers", "points": 44, "rank": "Corps", "hp": 1, "courage": 1, "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Steady"},
                {"name": "Imperial Death Troopers", "points": 72, "rank": "Special Forces", "hp": 1, "courage": 2, "slots": ["Heavy Weapon", "Training", "Comms", "Gear", "Grenades"], "info": "Disciplined 1, Precise 2"},
                {"name": "Scout Troopers (Strike Team)", "points": 20, "rank": "Special Forces", "hp": 1, "courage": 2, "slots": ["Heavy Weapon", "Training", "Gear", "Grenades"], "info": "Low Profile, Scout 1"},
                {"name": "74-Z Speeder Bikes", "points": 70, "rank": "Support", "hp": 3, "courage": 2, "slots": ["Comms"], "info": "Cover 1, Speeder 1"},
                {"name": "Dewback Rider", "points": 70, "rank": "Support", "hp": 6, "courage": 2, "slots": ["Training", "Comms", "Armament"], "info": "Armor 1, Relentless"},
                {"name": "AT-ST", "points": 155, "rank": "Heavy", "hp": 11, "courage": 8, "slots": ["Pilot", "Hardpoint", "Hardpoint", "Comms"], "info": "Armor, Arsenal 2"},
            ],
            "Rebellenallianz": [
                {"name": "Luke Skywalker (Commander)", "points": 160, "rank": "Commander", "hp": 6, "courage": 3, "slots": ["Force", "Force", "Gear"], "info": "Jump 1, Charge, Deflect"},
                {"name": "Leia Organa", "points": 85, "rank": "Commander", "hp": 4, "courage": 2, "slots": ["Command", "Gear"], "info": "Inspire 2, Nimble, Take Cover 2"},
                {"name": "Han Solo", "points": 100, "rank": "Commander", "hp": 6, "courage": 2, "slots": ["Command", "Training", "Gear"], "info": "Gunslinger, Low Profile"},
                {"name": "Rebel Troopers", "points": 40, "rank": "Corps", "hp": 1, "courage": 1, "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Nimble"},
                {"name": "Rebel Veterans", "points": 48, "rank": "Corps", "hp": 1, "courage": 1, "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Defend 1, Coordinate"},
                {"name": "Rebel Commandos", "points": 48, "rank": "Special Forces", "hp": 1, "courage": 2, "slots": ["Heavy Weapon", "Training", "Gear", "Grenades"], "info": "Low Profile, Scout 2"},
                {"name": "Wookiee Warriors", "points": 69, "rank": "Special Forces", "hp": 3, "courage": 2, "slots": ["Heavy Weapon", "Training", "Training", "Gear", "Grenades"], "info": "Charge, Duelist, Indomitable"},
                {"name": "AT-RT", "points": 55, "rank": "Support", "hp": 6, "courage": 4, "slots": ["Hardpoint", "Comms"], "info": "Armor, Climbing Vehicle"},
                {"name": "T-47 Airspeeder", "points": 130, "rank": "Heavy", "hp": 7, "courage": 5, "slots": ["Pilot", "Hardpoint", "Comms"], "info": "Armor, Arsenal 2, Speeder 2"},
            ],
            "Separatistenallianz": [
                {"name": "General Grievous", "points": 155, "rank": "Commander", "hp": 8, "courage": 2, "slots": ["Command", "Training", "Gear", "Armament"], "info": "Arsenal 2, Block, Jedi Hunter"},
                {"name": "Count Dooku", "points": 195, "rank": "Commander", "hp": 5, "courage": "-", "slots": ["Force", "Force", "Force", "Command"], "info": "Cunning, Deflect, Immune: Pierce"},
                {"name": "Super Tactical Droid", "points": 90, "rank": "Commander", "hp": 5, "courage": 2, "slots": ["Command", "Command", "Comms", "Gear"], "info": "Strategist 1, Direct: AI"},
                {"name": "B1 Battle Droids", "points": 38, "rank": "Corps", "hp": 1, "courage": 1, "slots": ["Heavy Weapon", "Personnel", "Comms", "Electrobinoculars"], "info": "AI: Attack, Coordinate: Droid"},
                {"name": "B2 Super Battle Droids", "points": 45, "rank": "Corps", "hp": 2, "courage": 1, "slots": ["Heavy Weapon", "Personnel", "Comms"], "info": "AI: Attack, Armor 1"},
                {"name": "BX-Series Droid Commandos", "points": 68, "rank": "Special Forces", "hp": 1, "courage": 2, "slots": ["Heavy Weapon", "Training", "Gear", "Grenades", "Comms"], "info": "AI: Move/Attack, Scale, Scout 3"},
                {"name": "Droidekas", "points": 75, "rank": "Support", "hp": 4, "courage": 2, "slots": ["Comms"], "info": "Shields 4, Wheel Mode"},
                {"name": "STAP Riders", "points": 70, "rank": "Support", "hp": 3, "courage": 2, "slots": ["Comms"], "info": "Cover 1, Speeder 1"},
                {"name": "AAT Trade Federation Tank", "points": 175, "rank": "Heavy", "hp": 9, "courage": 6, "slots": ["Pilot", "Hardpoint", "Comms"], "info": "Armor, Arsenal 2"},
            ],
            "Galaktische Republik": [
                {"name": "Obi-Wan Kenobi", "points": 170, "rank": "Commander", "hp": 6, "courage": 3, "slots": ["Force", "Force", "Command", "Training"], "info": "Guardian 3, Soresu Mastery"},
                {"name": "Clone Captain Rex", "points": 95, "rank": "Commander", "hp": 5, "courage": 2, "slots": ["Command", "Training", "Gear", "Grenades"], "info": "Gunslinger, Scout 1, Tactical 1"},
                {"name": "Anakin Skywalker", "points": 155, "rank": "Commander", "hp": 6, "courage": 3, "slots": ["Force", "Force", "Training"], "info": "Deflect, Djem So Mastery, Tempted"},
                {"name": "Phase I Clone Troopers", "points": 52, "rank": "Corps", "hp": 1, "courage": 1, "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Fire Support"},
                {"name": "Phase II Clone Troopers", "points": 60, "rank": "Corps", "hp": 1, "courage": 2, "slots": ["Heavy Weapon", "Personnel", "Training", "Gear"], "info": "Reliable 1"},
                {"name": "ARC Troopers", "points": 72, "rank": "Special Forces", "hp": 1, "courage": 2, "slots": ["Heavy Weapon", "Personnel", "Training", "Gear"], "info": "Impervious, Jetpacks, Tactical 1"},
                {"name": "BARC Speeder", "points": 55, "rank": "Support", "hp": 5, "courage": 3, "slots": ["Crew", "Comms"], "info": "Cover 1, Speeder 1"},
                {"name": "AT-RT (Republic)", "points": 55, "rank": "Support", "hp": 6, "courage": 4, "slots": ["Hardpoint", "Comms"], "info": "Armor, Climbing Vehicle"},
                {"name": "TX-130 Saber Tank", "points": 170, "rank": "Heavy", "hp": 9, "courage": 5, "slots": ["Pilot", "Hardpoint", "Comms"], "info": "Armor, Arsenal 2"},
            ],
             "Schattenkollektiv": [
                 {"name": "Maul (Shadow Collective)", "points": 160, "rank": "Commander", "hp": 6, "courage": 3, "slots": ["Force", "Force", "Command", "Armament"], "info": "Juyo Mastery, Allies of Convenience"},
                 {"name": "Pyke Syndicate Capo", "points": 45, "rank": "Commander", "hp": 4, "courage": 2, "slots": ["Command", "Gear", "Armament"], "info": "Aid, Danger Sense 2"},
                 {"name": "Black Sun Enforcers", "points": 48, "rank": "Corps", "hp": 1, "courage": 2, "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Dauntless, Indomitable"},
                 {"name": "Pyke Syndicate Foot Soldiers", "points": 40, "rank": "Corps", "hp": 1, "courage": 1, "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Danger Sense 2, Independent: Dodge 1"},
            ]
        }

    def get_valid_upgrades(self, slot_type, unit_name, faction_name):
        """
        Filtert Upgrades basierend auf Slot, Fraktion und Einheitenbeschränkung.
        """
        valid = []
        for upg in self.upgrades:
            # 1. Passt der Typ?
            if upg["type"] != slot_type: 
                continue
            
            # 2. Prüfe Beschränkungen (Restrictions)
            restrictions = upg.get("restricted_to")
            
            if restrictions is None:
                # Keine Beschränkung -> Erlaubt
                valid.append(upg)
            else:
                # Ist der Einheiten-Name ODER Fraktions-Name in der Liste?
                if unit_name in restrictions or faction_name in restrictions:
                    valid.append(upg)
                # Fraktionsübergreifende Logik (Dunkle/Helle Seite)
                elif faction_name in ["Galaktisches Imperium", "Separatistenallianz", "Schattenkollektiv"] and "Dunkle Seite" in restrictions:
                    valid.append(upg)
                elif faction_name in ["Rebellenallianz", "Galaktische Republik"] and "Helle Seite" in restrictions:
                    valid.append(upg)
                    
        return valid

# =============================================================================
# TEIL 2: DIE BENUTZEROBERFLÄCHE (GUI) UND SPEICHER-LOGIK
# =============================================================================

class LegionArmyBuilder:
    def __init__(self, root):
        self.db = LegionDatabase()
        self.root = root
        self.root.title("SW Legion: Army Architect v4.0 (Save/Load)")
        self.root.geometry("1200x800")

        self.current_army_list = [] 
        self.current_faction = tk.StringVar()
        self.total_points = 0
        
        # Basis-Ordner für Speicherstände erstellen
        self.base_dir = "Armeen"
        if not os.path.exists(self.base_dir):
            try:
                os.makedirs(self.base_dir)
            except OSError as e:
                messagebox.showerror("Fehler", f"Konnte Ordner nicht erstellen: {e}")

        self.setup_ui()

    def setup_ui(self):
        # Haupt-Container (Split Panel)
        paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # --- LINKE SEITE: BIBLIOTHEK ---
        left_frame = tk.Frame(paned, padx=10, pady=10)
        paned.add(left_frame, width=500)

        # 1. Fraktion Auswahl
        tk.Label(left_frame, text="1. Fraktion wählen:", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.cb_faction = ttk.Combobox(left_frame, textvariable=self.current_faction, values=list(self.db.units.keys()), state="readonly")
        self.cb_faction.pack(fill="x", pady=5)
        self.cb_faction.bind("<<ComboboxSelected>>", self.update_unit_list)

        # 2. Einheiten Liste
        tk.Label(left_frame, text="2. Einheit wählen:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(15, 0))
        
        cols = ("Name", "Punkte", "Rang")
        self.tree_units = ttk.Treeview(left_frame, columns=cols, show="headings", height=20)
        self.tree_units.heading("Name", text="Einheit")
        self.tree_units.heading("Punkte", text="Pkt")
        self.tree_units.heading("Rang", text="Rang")
        self.tree_units.column("Name", width=250)
        self.tree_units.column("Punkte", width=50, anchor="center")
        self.tree_units.column("Rang", width=100)
        self.tree_units.pack(fill="both", expand=True, pady=5)
        
        # Scrollbar für Einheiten
        sb_units = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree_units.yview)
        sb_units.place(relx=0.96, rely=0.2, relheight=0.4) # Grobe Positionierung
        self.tree_units.configure(yscrollcommand=sb_units.set)

        self.tree_units.bind("<<TreeviewSelect>>", self.show_unit_stats)

        # 3. Info Box
        self.lbl_stats = tk.Label(left_frame, text="Wähle eine Einheit für Details...", justify=tk.LEFT, bg="#e1e1e1", relief=tk.SUNKEN, padx=10, pady=10, font=("Consolas", 9))
        self.lbl_stats.pack(fill="x", pady=5)

        # 4. Hinzufügen Button
        btn_config = tk.Button(left_frame, text="Einheit anpassen & hinzufügen >", bg="#2196F3", fg="white", font=("Segoe UI", 11, "bold"), command=self.open_config_window)
        btn_config.pack(fill="x", pady=10)

        # --- RECHTE SEITE: ARMEE LISTE ---
        right_frame = tk.Frame(paned, bg="#f0f0f0", padx=10, pady=10)
        paned.add(right_frame)

        # Header mit Load/Save Buttons
        top_btn_frame = tk.Frame(right_frame, bg="#f0f0f0")
        top_btn_frame.pack(fill="x", pady=(0, 10))

        tk.Label(top_btn_frame, text="Deine Armeeliste", bg="#f0f0f0", font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)
        
        btn_load = tk.Button(top_btn_frame, text="📂 Laden", command=self.load_army, bg="#FF9800", fg="white", font=("Segoe UI", 9, "bold"))
        btn_load.pack(side=tk.RIGHT, padx=5)
        
        btn_save = tk.Button(top_btn_frame, text="💾 Speichern", command=self.save_army, bg="#009688", fg="white", font=("Segoe UI", 9, "bold"))
        btn_save.pack(side=tk.RIGHT, padx=5)

        # Armee Liste (Treeview)
        army_cols = ("ID", "Einheit", "Upgrades", "Punkte")
        self.tree_army = ttk.Treeview(right_frame, columns=army_cols, show="headings")
        self.tree_army.heading("ID", text="#")
        self.tree_army.heading("Einheit", text="Einheit")
        self.tree_army.heading("Upgrades", text="Ausrüstung")
        self.tree_army.heading("Punkte", text="Kosten")
        
        self.tree_army.column("ID", width=30, anchor="center")
        self.tree_army.column("Einheit", width=180)
        self.tree_army.column("Upgrades", width=300)
        self.tree_army.column("Punkte", width=60, anchor="center")
        self.tree_army.pack(fill="both", expand=True, pady=5)

        # Untere Buttons
        btn_frame = tk.Frame(right_frame, bg="#f0f0f0")
        btn_frame.pack(fill="x")
        
        btn_del = tk.Button(btn_frame, text="Entfernen", command=self.remove_unit, bg="#ffcccc")
        btn_del.pack(side=tk.LEFT)

        # Gesamtpunkte
        self.lbl_total = tk.Label(right_frame, text="Gesamtpunkte: 0 / 800", font=("Segoe UI", 16, "bold"), bg="#f0f0f0", fg="#333")
        self.lbl_total.pack(pady=20)

        # Export Text
        btn_export = tk.Button(right_frame, text="Liste in Zwischenablage kopieren (Text)", command=self.copy_to_clipboard, bg="#4CAF50", fg="white", height=2, font=("Segoe UI", 10, "bold"))
        btn_export.pack(fill="x")

    # --- LOGIK: SPEICHERN & LADEN ---

    def save_army(self):
        if not self.current_army_list:
            messagebox.showwarning("Fehler", "Die Liste ist leer!")
            return
        
        faction = self.current_faction.get()
        if not faction:
            messagebox.showwarning("Fehler", "Keine Fraktion gewählt!")
            return

        # Ordner Struktur sicherstellen: Armeen/Fraktion/
        # Umlaute oder Leerzeichen im Pfad sind hier meist kein Problem, 
        # aber wir nutzen os.path.join für Sicherheit.
        save_dir = os.path.join(self.base_dir, faction)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Dialog öffnen
        file_path = filedialog.asksaveasfilename(
            initialdir=save_dir,
            title="Armee speichern",
            defaultextension=".json",
            filetypes=[("JSON Dateien", "*.json"), ("Alle Dateien", "*.*")]
        )

        if file_path:
            # Datenpaket schnüren
            save_data = {
                "faction": faction,
                "total_points": self.total_points,
                "army": self.current_army_list
            }
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Erfolg", f"Armee erfolgreich gespeichert unter:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Konnte nicht speichern: {e}")

    def load_army(self):
        # Dialog startet im Basis-Ordner
        file_path = filedialog.askopenfilename(
            initialdir=self.base_dir,
            title="Armee laden",
            filetypes=[("JSON Dateien", "*.json")]
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Daten Validieren
                faction = data.get("faction")
                army_list = data.get("army")

                if faction and army_list is not None:
                    # 1. Fraktion setzen
                    self.current_faction.set(faction)
                    # 2. GUI Links aktualisieren (damit man Einheiten hinzufügen kann)
                    self.update_unit_list()
                    # 3. Armee setzen
                    self.current_army_list = army_list
                    # 4. GUI Rechts aktualisieren
                    self.refresh_army_view()
                    
                    messagebox.showinfo("Geladen", f"Armee '{faction}' geladen. Du kannst sie nun bearbeiten!")
                else:
                    messagebox.showerror("Fehler", "Ungültiges Dateiformat. JSON enthält keine Fraktion oder Armee.")

            except Exception as e:
                messagebox.showerror("Fehler", f"Konnte Datei nicht lesen: {e}")

    # --- GUI UPDATE FUNKTIONEN ---

    def update_unit_list(self, event=None):
        # Treeview leeren
        for item in self.tree_units.get_children():
            self.tree_units.delete(item)
        
        faction = self.current_faction.get()
        if faction in self.db.units:
            units = self.db.units[faction]
            # Sortierreihenfolge definieren
            order = {"Commander": 1, "Operative": 2, "Corps": 3, "Special Forces": 4, "Support": 5, "Heavy": 6}
            
            # Sortieren
            units_sorted = sorted(units, key=lambda x: order.get(x["rank"], 99))
            
            # Einfügen
            for u in units_sorted:
                self.tree_units.insert("", "end", values=(u["name"], u["points"], u["rank"]))

    def show_unit_stats(self, event):
        selected = self.tree_units.focus()
        if not selected: return
        
        vals = self.tree_units.item(selected, "values")
        name = vals[0]
        faction = self.current_faction.get()
        
        # Einheit in DB suchen
        unit_data = next((u for u in self.db.units[faction] if u["name"] == name), None)
        
        if unit_data:
            txt = (f"Lebenspunkte: {unit_data['hp']} | Mut: {unit_data['courage']}\n"
                   f"Slots: {', '.join(unit_data['slots'])}\n"
                   f"Info: {unit_data['info']}")
            self.lbl_stats.config(text=txt)

    def open_config_window(self):
        selected = self.tree_units.focus()
        if not selected:
            messagebox.showwarning("Achtung", "Bitte wähle zuerst links eine Einheit aus.")
            return
            
        vals = self.tree_units.item(selected, "values")
        unit_name = vals[0]
        faction = self.current_faction.get()
        unit_data = next((u for u in self.db.units[faction] if u["name"] == unit_name), None)
        
        if not unit_data: return

        # --- KONFIGURATIONS FENSTER (POPUP) ---
        top = tk.Toplevel(self.root)
        top.title(f"Ausrüstung: {unit_name}")
        top.geometry("550x650")
        
        tk.Label(top, text=f"Konfiguration: {unit_name}", font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        # Scrollbarer Bereich (Canvas) für viele Slots
        canvas = tk.Canvas(top)
        scrollbar = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        selectors = [] # Speichert Referenzen zu den Dropdowns
        
        # Für jeden Slot der Einheit ein Dropdown erstellen
        for slot in unit_data["slots"]:
            frame = tk.Frame(scroll_frame, pady=5, padx=5, relief=tk.GROOVE, bd=1)
            frame.pack(fill="x", padx=10, pady=2)
            
            tk.Label(frame, text=f"{slot}:", width=15, anchor="w", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
            
            # --- INTELLIGENTER FILTER ---
            valid_upgrades = self.db.get_valid_upgrades(slot, unit_name, faction)
            
            options = ["--- Leer ---"]
            upgrade_map = {} # Map um vom Namen auf die Punkte zu kommen
            
            for upg in valid_upgrades:
                display_str = f"{upg['name']} ({upg['points']} Pkt)"
                options.append(display_str)
                upgrade_map[display_str] = upg
            
            var = tk.StringVar(value=options[0])
            cb = ttk.Combobox(frame, textvariable=var, values=options, state="readonly", width=40)
            cb.pack(side=tk.RIGHT, fill="x", expand=True)
            
            selectors.append({"var": var, "map": upgrade_map})

        def add_confirmed():
            total_cost = unit_data["points"]
            chosen_upgrades_list = []
            
            for sel in selectors:
                val = sel["var"].get()
                if val != "--- Leer ---":
                    upg_data = sel["map"][val]
                    total_cost += upg_data["points"]
                    chosen_upgrades_list.append(val) # Speichert "Name (Punkte)"
            
            # Zur Armee hinzufügen
            self.current_army_list.append({
                "name": unit_name,
                "upgrades": chosen_upgrades_list,
                "points": total_cost,
                "base_points": unit_data["points"]
            })
            self.refresh_army_view()
            top.destroy()

        tk.Button(top, text="HINZUFÜGEN", bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold"), command=add_confirmed).pack(side="bottom", fill="x", pady=10, padx=10)

    def refresh_army_view(self):
        # Liste leeren
        for item in self.tree_army.get_children():
            self.tree_army.delete(item)
            
        self.total_points = 0
        
        for idx, unit in enumerate(self.current_army_list):
            upg_str = ", ".join(unit["upgrades"]) if unit["upgrades"] else "-"
            self.tree_army.insert("", "end", values=(idx+1, unit["name"], upg_str, unit["points"]))
            self.total_points += unit["points"]
            
        self.lbl_total.config(text=f"Gesamtpunkte: {self.total_points} / 800")
        
        # Farbliche Warnung bei Überpunktzahl
        if self.total_points > 800:
            self.lbl_total.config(fg="red")
        else:
            self.lbl_total.config(fg="#333")

    def remove_unit(self):
        selected = self.tree_army.focus()
        if not selected: return
        idx = self.tree_army.index(selected)
        del self.current_army_list[idx]
        self.refresh_army_view()

    def copy_to_clipboard(self):
        if not self.current_army_list: return
        
        faction = self.current_faction.get() if self.current_faction.get() else "Unbekannt"
        text = f"STAR WARS LEGION LISTE\nFraktion: {faction}\nGesamtpunkte: {self.total_points}\n"
        text += "="*40 + "\n\n"
        
        for unit in self.current_army_list:
            text += f"• {unit['name']} ({unit['points']} Pkt)\n"
            if unit['upgrades']:
                for upg in unit['upgrades']:
                    text += f"   - {upg}\n"
            text += "\n"
            
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Kopiert", "Liste wurde in die Zwischenablage kopiert!")

# =============================================================================
# START
# =============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = LegionArmyBuilder(root)
    root.mainloop()