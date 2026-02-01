import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import random
import os
from LegionData import LegionDatabase

class GameCompanion:
    def __init__(self, root):
        self.db = LegionDatabase()
        self.root = root
        self.root.title("SW Legion: Game Companion & AI Simulator")
        self.root.geometry("1400x900")

        # Game State
        self.player_army = {"faction": "", "units": []}
        self.opponent_army = {"faction": "", "units": []}

        # Order Pool: Liste von Tupeln (UnitObject, "Player" oder "Opponent")
        self.order_pool = []
        self.active_unit = None
        self.active_side = None # "Player" oder "Opponent"

        self.setup_ui()

    def setup_ui(self):
        # Top Menü Leiste
        top_frame = tk.Frame(self.root, bg="#333", pady=5)
        top_frame.pack(fill="x")

        tk.Label(top_frame, text="Spiel-Begleiter", fg="white", bg="#333", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=10)

        btn_load_p = tk.Button(top_frame, text="Lade Spieler-Armee", bg="#2196F3", fg="white", command=lambda: self.load_army(True))
        btn_load_p.pack(side=tk.LEFT, padx=20)

        btn_load_o = tk.Button(top_frame, text="Lade Gegner-Armee (AI)", bg="#F44336", fg="white", command=lambda: self.load_army(False))
        btn_load_o.pack(side=tk.RIGHT, padx=20)

        self.ai_enabled = tk.BooleanVar(value=True)
        chk_ai = tk.Checkbutton(top_frame, text="AI Aktiv", variable=self.ai_enabled, bg="#333", fg="white", selectcolor="#555", font=("Segoe UI", 10))
        chk_ai.pack(side=tk.RIGHT, padx=5)

        # Haupt-Container
        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- LINKS: SPIELER ARMEE ---
        self.frame_player = tk.Frame(self.paned, width=300, relief=tk.SUNKEN, bd=1)
        self.paned.add(self.frame_player)
        tk.Label(self.frame_player, text="Spieler Armee", font=("Segoe UI", 12, "bold"), bg="#bbdefb", pady=5).pack(fill="x")
        self.tree_player = self.create_unit_tree(self.frame_player)

        # --- MITTE: SCHLACHTFELD / AKTIVITÄT ---
        self.frame_center = tk.Frame(self.paned, width=600, relief=tk.SUNKEN, bd=1, bg="#fafafa")
        self.paned.add(self.frame_center)

        # Initialer Bildschirm in der Mitte
        self.lbl_center_info = tk.Label(self.frame_center, text="Bitte Armeen laden und Spiel starten", font=("Segoe UI", 14), bg="#fafafa")
        self.lbl_center_info.place(relx=0.5, rely=0.4, anchor="center")

        # Start Button
        self.btn_start = tk.Button(self.frame_center, text="SPIEL STARTEN (Order Pool füllen)", font=("Segoe UI", 14, "bold"), bg="#4CAF50", fg="white", command=self.init_game)
        self.btn_start.place(relx=0.5, rely=0.5, anchor="center")

        # --- RECHTS: GEGNER ARMEE ---
        self.frame_opponent = tk.Frame(self.paned, width=300, relief=tk.SUNKEN, bd=1)
        self.paned.add(self.frame_opponent)
        tk.Label(self.frame_opponent, text="Gegner Armee (AI)", font=("Segoe UI", 12, "bold"), bg="#ffcdd2", pady=5).pack(fill="x")
        self.tree_opponent = self.create_unit_tree(self.frame_opponent)

    def create_unit_tree(self, parent):
        cols = ("Name", "Minis", "HP", "Status")
        tree = ttk.Treeview(parent, columns=cols, show="headings")
        tree.heading("Name", text="Einheit")
        tree.heading("Minis", text="Fig.")
        tree.heading("HP", text="HP")
        tree.heading("Status", text="Status")
        tree.column("Name", width=140)
        tree.column("Minis", width=30, anchor="center")
        tree.column("HP", width=40, anchor="center")
        tree.column("Status", width=60)
        tree.pack(fill="both", expand=True)
        return tree

    def load_army(self, is_player):
        initial_dir = "Armeen"
        if not os.path.exists(initial_dir):
            os.makedirs(initial_dir)

        file_path = filedialog.askopenfilename(initialdir=initial_dir, title="Armee laden", filetypes=[("JSON", "*.json")])
        if not file_path: return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            faction = data.get("faction")
            army_list = data.get("army", [])

            # Einheiten mit DB-Stats anreichern
            enriched_units = []
            for item in army_list:
                # Originale Daten aus DB holen
                db_unit = self.find_unit_in_db(item["name"], faction)
                if db_unit:
                    # Kombiniere gespeicherte Daten (Upgrades, Punkte) mit statischen Daten (Waffen, Speed...)
                    full_unit = {**db_unit, **item} # Merge
                    # Zustand hinzufügen
                    full_unit["current_hp"] = full_unit["hp"]
                    full_unit["activated"] = False
                    full_unit["suppression"] = 0

                    # Minis berechnen falls nicht im Save (Kompatibilität)
                    if "minis" not in full_unit:
                        base = db_unit.get("minis", 1)
                        extra = 0
                        # Check upgrades in 'item' (das gespeicherte Objekt hat 'upgrades' Liste von Strings)
                        # Leider haben wir hier nur Strings "Name (Punkte)". Wir müssten matchen.
                        # Vereinfachung: Wir nehmen base wenn nicht gespeichert.
                        full_unit["minis"] = base

                    enriched_units.append(full_unit)
                else:
                    print(f"Warnung: Einheit {item['name']} nicht in DB gefunden.")

            # Speichern
            if is_player:
                self.player_army = {"faction": faction, "units": enriched_units}
                self.update_tree(self.tree_player, self.player_army["units"])
            else:
                self.opponent_army = {"faction": faction, "units": enriched_units}
                self.update_tree(self.tree_opponent, self.opponent_army["units"])

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden: {e}")

    def find_unit_in_db(self, name, faction):
        if faction in self.db.units:
            for u in self.db.units[faction]:
                if u["name"] == name:
                    return u
        return None

    def update_tree(self, tree, units):
        for item in tree.get_children():
            tree.delete(item)
        for u in units:
            status = "Bereit" if not u["activated"] else "Aktiviert"
            minis = u.get("minis", 1)
            tree.insert("", "end", values=(u["name"], minis, f"{u['current_hp']}/{u['hp']}", status))

    def init_game(self):
        if not self.player_army["units"] and not self.opponent_army["units"]:
            messagebox.showwarning("Fehler", "Bitte lade mindestens eine Armee.")
            return

        # UI aufräumen
        self.lbl_center_info.destroy()
        self.btn_start.destroy()

        # Game Controls erstellen
        self.create_game_controls()

        # Runde starten
        self.start_round()

    def create_game_controls(self):
        # Header für Phase
        self.lbl_phase = tk.Label(self.frame_center, text="Bereit zum Start", font=("Segoe UI", 16, "bold"), bg="#fafafa")
        self.lbl_phase.pack(pady=10)

        # Draw Button
        self.btn_draw = tk.Button(self.frame_center, text="BEFEHL ZIEHEN (Order Token)", font=("Segoe UI", 12, "bold"), bg="#FF9800", fg="white", command=self.draw_order)
        self.btn_draw.pack(pady=10)

        # Active Unit Info Frame
        self.frame_active = tk.Frame(self.frame_center, bg="white", relief=tk.RIDGE, bd=2)
        self.frame_active.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(self.frame_active, text="Aktive Einheit:", font=("Segoe UI", 10)).pack(anchor="w", padx=5)
        self.lbl_active_name = tk.Label(self.frame_active, text="-", font=("Segoe UI", 14, "bold"), bg="white", fg="#2196F3")
        self.lbl_active_name.pack(anchor="w", padx=5)

        self.lbl_active_stats = tk.Label(self.frame_active, text="", font=("Consolas", 10), justify=tk.LEFT, bg="white")
        self.lbl_active_stats.pack(anchor="w", padx=5, pady=5)

        # Action Buttons (werden aktiviert wenn Einheit da ist)
        self.frame_actions = tk.Frame(self.frame_active, bg="white")
        self.frame_actions.pack(fill="x", pady=10)

        # Attack Button (Platzhalter für nächsten Schritt)
        self.btn_attack = tk.Button(self.frame_actions, text="⚔ ANGRIFF", bg="#F44336", fg="white", state=tk.DISABLED)
        self.btn_attack.pack(side=tk.LEFT, padx=10)

    def start_round(self):
        self.order_pool = []

        # Alle Einheiten in den Pool
        # Wir speichern: {"unit": unit_dict, "side": "Player"|"Opponent"}
        for u in self.player_army["units"]:
            if u["current_hp"] > 0:
                self.order_pool.append({"unit": u, "side": "Player"})
                u["activated"] = False

        for u in self.opponent_army["units"]:
            if u["current_hp"] > 0:
                self.order_pool.append({"unit": u, "side": "Opponent"})
                u["activated"] = False

        random.shuffle(self.order_pool)
        self.update_trees()
        self.lbl_phase.config(text=f"Neue Runde! {len(self.order_pool)} Befehle im Pool.")
        self.btn_draw.config(state=tk.NORMAL, text="BEFEHL ZIEHEN")

        # Reset Active View
        self.lbl_active_name.config(text="-")
        self.lbl_active_stats.config(text="")
        self.active_unit = None
        self.btn_attack.config(state=tk.DISABLED)

    def draw_order(self):
        if not self.order_pool:
            ans = messagebox.askyesno("Rundenende", "Der Befehlspool ist leer. Neue Runde starten?")
            if ans:
                self.start_round()
            return

        # Ziehen
        drawn = self.order_pool.pop(0)
        unit = drawn["unit"]
        side = drawn["side"]

        self.active_unit = unit
        self.active_side = side
        unit["activated"] = True

        # UI Updates
        color = "#2196F3" if side == "Player" else "#F44336"
        self.lbl_active_name.config(text=f"{unit['name']} ({side})", fg=color)

        stats_text = (f"Bewegung: {unit.get('speed', '-')}\n"
                      f"Verteidigung: {unit.get('defense', '-')}\n"
                      f"HP: {unit['current_hp']}/{unit['hp']} | Mut: {unit['courage']}\n"
                      f"Keywords: {unit.get('info', '')}")
        self.lbl_active_stats.config(text=stats_text)

        # Update Trees (um 'Aktiviert' Status zu zeigen)
        self.update_trees()

        self.lbl_phase.config(text=f"Pool: {len(self.order_pool)} verbleibend")

        # Buttons aktivieren
        self.btn_attack.config(state=tk.NORMAL, command=self.open_attack_dialog)

        # AI LOGIC
        if side == "Opponent" and self.ai_enabled.get():
            intention = self.generate_ai_intention(unit)
            self.show_ai_intention(unit["name"], intention)

    def generate_ai_intention(self, unit):
        # Einfache Logik basierend auf Einheitentyp
        # Check ob Nahkämpfer (Range 0-1 Waffe vorhanden?)
        is_melee = False
        max_range = 0
        if "weapons" in unit:
            for w in unit["weapons"]:
                r = w["range"][1]
                if r > max_range: max_range = r
                if r == 1 and w["range"][0] == 0: is_melee = True

        hp_ratio = unit["current_hp"] / unit["hp"]

        actions = []

        # Logik Baum
        if is_melee and max_range < 2:
            # Nahkämpfer
            if hp_ratio > 0.5:
                actions.append("Bewegung (Doppel) auf nächsten Feind zu")
                actions.append("Angriff (Nahkampf) wenn möglich")
            else:
                actions.append("Bewegung in Deckung")
                actions.append("Ausweichen (Dodge)")
        else:
            # Fernkämpfer
            if hp_ratio < 0.3:
                 actions.append("Bewegung (Rückzug/Deckung)")
                 actions.append("Angriff auf nächste Bedrohung")
            else:
                 # Standard
                 actions.append("Zielen (Aim)")
                 actions.append("Angriff auf Einheit mit wenig Deckung")

        # Zufallselement
        if not actions:
            actions = ["Bewegung", "Angriff"]

        return " -> ".join(actions)

    def show_ai_intention(self, name, text):
        top = tk.Toplevel(self.root)
        top.title("AI Gegner Planung")
        top.geometry("400x200")
        top.configure(bg="#ffebee")

        tk.Label(top, text=f"🤖 AI: {name}", font=("Segoe UI", 14, "bold"), bg="#ffebee").pack(pady=10)
        tk.Label(top, text="Die AI plant folgenden Zug:", bg="#ffebee").pack()

        msg = tk.Message(top, text=text, font=("Segoe UI", 12), bg="white", width=350, padx=10, pady=10, relief=tk.RIDGE)
        msg.pack(pady=10)

        tk.Button(top, text="OK", command=top.destroy, bg="#F44336", fg="white", width=10).pack(pady=10)

    def update_trees(self):
        if self.player_army["units"]:
            self.update_tree(self.tree_player, self.player_army["units"])
        if self.opponent_army["units"]:
            self.update_tree(self.tree_opponent, self.opponent_army["units"])

    def open_attack_dialog(self):
        if not self.active_unit: return

        # Dialog
        top = tk.Toplevel(self.root)
        top.title("Angriff durchführen")
        top.geometry("600x700")

        unit = self.active_unit

        tk.Label(top, text=f"Angreifer: {unit['name']}", font=("Segoe UI", 12, "bold")).pack(pady=5)

        # 1. WAFFEN WAHL
        frame_weapons = tk.LabelFrame(top, text="1. Waffen wählen", padx=10, pady=10)
        frame_weapons.pack(fill="x", padx=10, pady=5)

        weapon_vars = []
        if "weapons" in unit:
            for w in unit["weapons"]:
                var = tk.BooleanVar()
                chk = tk.Checkbutton(frame_weapons, text=f"{w['name']} (Reichweite {w['range'][0]}-{w['range'][1]})", variable=var)
                chk.pack(anchor="w")
                # Stats anzeigen
                dice_str = " | ".join([f"{k}: {v}" for k, v in w['dice'].items() if v > 0])
                tk.Label(frame_weapons, text=f"   Würfel: {dice_str} | Keywords: {', '.join(w.get('keywords', []))}", font=("Consolas", 8), fg="#555").pack(anchor="w")
                weapon_vars.append({"var": var, "data": w})
        else:
            tk.Label(frame_weapons, text="Keine Waffen definiert!").pack()

        # 2. ZIEL WAHL
        frame_target = tk.LabelFrame(top, text="2. Ziel & Verteidigung", padx=10, pady=10)
        frame_target.pack(fill="x", padx=10, pady=5)

        # Ziele finden (Gegner Seite)
        targets = self.opponent_army["units"] if self.active_side == "Player" else self.player_army["units"]
        target_names = [u["name"] for u in targets if u["current_hp"] > 0]

        tk.Label(frame_target, text="Ziel wählen:").grid(row=0, column=0, sticky="w")
        cb_target = ttk.Combobox(frame_target, values=target_names, state="readonly")
        cb_target.grid(row=0, column=1, sticky="ew")

        # Manuelle Overrides
        tk.Label(frame_target, text="Verteidigungswürfel:").grid(row=1, column=0, sticky="w", pady=5)
        var_def_die = tk.StringVar(value="White")
        cb_def = ttk.Combobox(frame_target, textvariable=var_def_die, values=["White", "Red"], state="readonly", width=10)
        cb_def.grid(row=1, column=1, sticky="w")

        # Auto-Fill Verteidigungswürfel bei Zielwahl
        def on_target_select(event):
            name = cb_target.get()
            target_unit = next((u for u in targets if u["name"] == name), None)
            if target_unit:
                d_die = target_unit.get("defense", "White")
                var_def_die.set(d_die)
        cb_target.bind("<<ComboboxSelected>>", on_target_select)

        # Deckung / Token
        tk.Label(frame_target, text="Deckung (Cover):").grid(row=2, column=0, sticky="w")
        var_cover = tk.IntVar(value=0)
        tk.Radiobutton(frame_target, text="Keine", variable=var_cover, value=0).grid(row=2, column=1, sticky="w")
        tk.Radiobutton(frame_target, text="Leicht (1)", variable=var_cover, value=1).grid(row=2, column=2, sticky="w")
        tk.Radiobutton(frame_target, text="Schwer (2)", variable=var_cover, value=2).grid(row=2, column=3, sticky="w")

        tk.Label(frame_target, text="Ausweichen-Marker (Dodge):").grid(row=3, column=0, sticky="w")
        var_dodge = tk.IntVar(value=0)
        tk.Spinbox(frame_target, from_=0, to=10, textvariable=var_dodge, width=5).grid(row=3, column=1, sticky="w")

        tk.Label(frame_target, text="Zielen-Marker (Aim) [Angreifer]:").grid(row=4, column=0, sticky="w", pady=(10,0))
        var_aim = tk.IntVar(value=0)
        tk.Spinbox(frame_target, from_=0, to=10, textvariable=var_aim, width=5).grid(row=4, column=1, sticky="w", pady=(10,0))

        # 3. ERGEBNIS BEREICH
        frame_result = tk.LabelFrame(top, text="3. Ergebnis", padx=10, pady=10, bg="#e0f7fa")
        frame_result.pack(fill="x", padx=10, pady=10)

        lbl_log = tk.Label(frame_result, text="Drücke 'WÜRFELN'...", bg="#e0f7fa", justify=tk.LEFT, font=("Consolas", 10))
        lbl_log.pack(anchor="w")

        # LOGIK
        def roll_attack():
            # 1. Pool bilden
            pool = {"red": 0, "black": 0, "white": 0}
            keywords = []
            selected_weapons = [w for w in weapon_vars if w["var"].get()]

            if not selected_weapons:
                messagebox.showwarning("Fehler", "Keine Waffe gewählt!")
                return

            for w in selected_weapons:
                wd = w["data"]
                for color, count in wd["dice"].items():
                    pool[color] += count
                if "keywords" in wd:
                    keywords.extend(wd["keywords"])

            # WÜRFELN (Angriff)
            results = {"crit": 0, "hit": 0, "surge": 0, "blank": 0}

            def roll_legion_atk(color):
                r = random.randint(1, 8)
                if color == "red":
                    # 1 Crit, 6 Hit (2-7), 1 Surge (8) - Red has no blank!
                    if r == 1: return "crit"
                    if 2 <= r <= 7: return "hit"
                    return "surge"
                if color == "black":
                    # 1 Crit, 3 Hit (2-4), 1 Surge (5), 3 Blank (6-8)
                    if r == 1: return "crit"
                    if 2 <= r <= 4: return "hit"
                    if r == 5: return "surge"
                    return "blank"
                if color == "white":
                    # 1 Crit, 1 Hit (2), 1 Surge (3), 5 Blank (4-8)
                    if r == 1: return "crit"
                    if r == 2: return "hit"
                    if r == 3: return "surge"
                    return "blank"
                return "blank"

            # Offensive Surge Conversion
            # Check unit surge chart
            surge_chart = unit.get("surge", {})
            atk_surge = surge_chart.get("attack") # "hit", "crit" oder None
            aims = var_aim.get()
            for color, count in pool.items():
                for _ in range(count):
                    results[roll_legion_atk(color)] += 1

            log_text = f"Wurf: {results}\n"

            # Apply Aim (Reroll blanks and surges if no surge conversion?)
            if aims > 0:
                # Strategie: Reroll Blanks.
                dice_to_reroll = min(results["blank"], aims * 2)
                if dice_to_reroll > 0:
                     log_text += f"Zielen: {dice_to_reroll} Blanks neu...\n"
                     results["blank"] -= dice_to_reroll
                     choices = []
                     for c, n in pool.items(): choices.extend([c]*n)
                     for _ in range(dice_to_reroll):
                         results[roll_legion_atk(random.choice(choices))] += 1
                     log_text += f"Nach Reroll: {results}\n"

            # Convert Surges
            if atk_surge == "hit":
                results["hit"] += results["surge"]
                log_text += f"Surge -> Hit ({results['surge']})\n"
                results["surge"] = 0
            elif atk_surge == "crit":
                results["crit"] += results["surge"]
                log_text += f"Surge -> Crit ({results['surge']})\n"
                results["surge"] = 0

            # Impact Keyword (Hit -> Crit gegen Armor)
            # Hier zu komplex, wir lassen Impact erstmal weg oder wenden es später an.

            total_hits = results["hit"] + results["crit"]
            log_text += f"TREFFER POOL: {total_hits} (Hits: {results['hit']}, Crits: {results['crit']})\n"

            # VERTEIDIGUNG
            # Cover abziehen (nur von Hits, nicht Crits)
            cover_val = var_cover.get()
            hits_removed_by_cover = min(results["hit"], cover_val)
            results["hit"] -= hits_removed_by_cover
            log_text += f"Deckung zieht {hits_removed_by_cover} Hits ab.\n"

            # Dodge Tokens (Dodge cancels 1 hit)
            dodges = var_dodge.get()
            hits_remaining = results["hit"] + results["crit"]
            if dodges > 0:
                removed = min(hits_remaining, dodges)
                log_text += f"Dodge ({dodges}) verhindert {removed} Treffer.\n"
                hits_remaining -= removed

            if hits_remaining <= 0:
                log_text += "ANGRIFF ABGEWEHRT (Keine Hits übrig)."
                lbl_log.config(text=log_text, fg="blue")
                return

            # Rüstungswürfe
            def_die_type = var_def_die.get() # Red / White
            # Defense Dice:
            # Red: 1 Block (1/6)? No.
            # Red Def: 3 Block (1-3), 1 Surge (4), 2 Blank (5-6)
            # White Def: 1 Block (1), 1 Surge (2), 4 Blank (3-6)

            blocks = 0
            def_surges = 0
            def_blanks = 0

            for _ in range(hits_remaining):
                r = random.randint(1, 6)
                if def_die_type == "Red":
                    if r <= 3: blocks += 1
                    elif r == 4: def_surges += 1
                    else: def_blanks += 1
                else: # White
                    if r == 1: blocks += 1
                    elif r == 2: def_surges += 1
                    else: def_blanks += 1

            log_text += f"\nVerteidigungswurf ({hits_remaining} Würfel {def_die_type}):\nBlocks: {blocks}, Surges: {def_surges}, Blanks: {def_blanks}\n"

            # Defense Surge Conversion
            # Wir müssen wissen, ob das Ziel Surge->Block hat.
            # Vereinfachung: Wir nehmen an, das Ziel hat es, wenn es in der DB steht.
            # Aber wir haben das Zielobjekt nicht zwingend geladen, wenn manuell gewählt.
            # Wir checken, ob wir target_unit gefunden haben
            target_unit = next((u for u in targets if u["name"] == cb_target.get()), None)
            has_surge_block = False
            if target_unit:
                sc = target_unit.get("surge", {})
                if sc.get("defense") == "block":
                    has_surge_block = True

            if has_surge_block:
                blocks += def_surges
                log_text += f"Surge -> Block ({def_surges})\n"

            # Pierce Keyword (Attacker)
            pierce_val = 0
            for k in keywords:
                if "Pierce" in k:
                    try:
                        pierce_val += int(k.split(" ")[1])
                    except: pass

            if pierce_val > 0 and blocks > 0:
                canceled = min(blocks, pierce_val)
                blocks -= canceled
                log_text += f"Pierce {pierce_val} bricht {canceled} Blocks!\n"

            # Schaden
            wounds = max(0, hits_remaining - blocks)
            log_text += f"\nSCHADEN: {wounds}"

            lbl_log.config(text=log_text, fg="red" if wounds > 0 else "green")

            # Apply Damage Button
            if wounds > 0 and target_unit:
                def apply_dmg():
                    target_unit["current_hp"] -= wounds
                    self.update_trees()
                    messagebox.showinfo("Update", f"{wounds} Schaden auf {target_unit['name']} angewendet.")
                    top.destroy()

                btn_apply = tk.Button(frame_result, text=f"{wounds} SCHADEN ANWENDEN", bg="red", fg="white", command=apply_dmg)
                btn_apply.pack(pady=5)

        tk.Button(top, text="WÜRFELN", command=roll_attack, font=("Segoe UI", 12, "bold"), bg="#2196F3", fg="white").pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = GameCompanion(root)
    root.mainloop()
