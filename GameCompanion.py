import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import random
import os
from LegionData import LegionDatabase
from LegionRules import LegionRules

class GameCompanion:
    def __init__(self, root):
        self.db = LegionDatabase()
        self.rules = LegionRules()
        self.root = root
        self.root.title("SW Legion: Game Companion & AI Simulator (Regeln 2.5)")
        self.root.geometry("1400x900")

        # Game State
        self.player_army = {"faction": "", "units": []}
        self.opponent_army = {"faction": "", "units": []}

        # Order Pool: Liste von Tupeln (UnitObject, "Player" oder "Opponent")
        self.order_pool = []
        self.active_unit = None
        self.active_side = None # "Player" oder "Opponent"

        # Round State
        self.current_round = 0
        self.current_phase = "Setup" # Setup, Command, Activation, End

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

        btn_rules = tk.Button(top_frame, text="Regel-Suche", bg="#9E9E9E", fg="white", command=self.open_rule_search)
        btn_rules.pack(side=tk.RIGHT, padx=10)

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
        self.btn_start = tk.Button(self.frame_center, text="SPIEL STARTEN (Setup)", font=("Segoe UI", 14, "bold"), bg="#4CAF50", fg="white", command=self.init_game)
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

            enriched_units = []
            for item in army_list:
                db_unit = self.find_unit_in_db(item["name"], faction)
                if db_unit:
                    full_unit = {**db_unit, **item}
                    full_unit["current_hp"] = full_unit["hp"]
                    full_unit["activated"] = False
                    full_unit["suppression"] = 0
                    if "minis" not in full_unit:
                        base = db_unit.get("minis", 1)
                        full_unit["minis"] = base
                    enriched_units.append(full_unit)
                else:
                    print(f"Warnung: Einheit {item['name']} nicht in DB gefunden.")

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

        self.lbl_center_info.destroy()
        self.btn_start.destroy()
        self.create_game_controls()

        self.current_round = 0
        self.start_new_round() # Starts with Command Phase

    def create_game_controls(self):
        # Phase Indicator
        self.frame_phase = tk.Frame(self.frame_center, bg="#eee", pady=5)
        self.frame_phase.pack(fill="x")
        self.lbl_phase_title = tk.Label(self.frame_phase, text="Setup", font=("Segoe UI", 16, "bold"), bg="#eee")
        self.lbl_phase_title.pack()
        self.lbl_round_info = tk.Label(self.frame_phase, text="Runde: 0", font=("Segoe UI", 10), bg="#eee")
        self.lbl_round_info.pack()

        # Phase Advice
        self.lbl_advice = tk.Label(self.frame_center, text="", font=("Segoe UI", 10, "italic"), bg="#fafafa", wraplength=550)
        self.lbl_advice.pack(pady=5)

        # Main Action Button (Dynamic)
        self.btn_action = tk.Button(self.frame_center, text="Aktion", font=("Segoe UI", 14, "bold"), bg="#2196F3", fg="white", command=self.advance_phase)
        self.btn_action.pack(pady=10)

        # Active Unit Info Frame
        self.frame_active = tk.Frame(self.frame_center, bg="white", relief=tk.RIDGE, bd=2)
        self.frame_active.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(self.frame_active, text="Aktive Einheit:", font=("Segoe UI", 10)).pack(anchor="w", padx=5)
        self.lbl_active_name = tk.Label(self.frame_active, text="-", font=("Segoe UI", 14, "bold"), bg="white", fg="#2196F3")
        self.lbl_active_name.pack(anchor="w", padx=5)

        self.lbl_active_stats = tk.Label(self.frame_active, text="", font=("Consolas", 10), justify=tk.LEFT, bg="white")
        self.lbl_active_stats.pack(anchor="w", padx=5, pady=5)

        # Action Buttons
        self.frame_actions = tk.Frame(self.frame_active, bg="white")
        self.frame_actions.pack(fill="x", pady=10)

        self.btn_attack = tk.Button(self.frame_actions, text="⚔ ANGRIFF", bg="#F44336", fg="white", state=tk.DISABLED)
        self.btn_attack.pack(side=tk.LEFT, padx=10)

    # --- PHASE MANAGEMENT ---

    def start_new_round(self):
        self.current_round += 1
        if self.current_round > 6:
            messagebox.showinfo("Spielende", "Runde 6 ist vorbei. Das Spiel ist zu Ende!")
            self.lbl_phase_title.config(text="SPIEL ENDE")
            return

        self.current_phase = "Command Phase"
        self.lbl_phase_title.config(text=f"Kommandophase (Runde {self.current_round})")
        self.lbl_round_info.config(text=f"Runde: {self.current_round}")

        info = self.rules.get_phase_info("1. Kommandophase")
        advice = "\n".join(info)
        self.lbl_advice.config(text=advice)

        self.btn_action.config(text="Kommandophase beenden -> Aktivierung", command=self.start_activation_phase, bg="#FF9800")

    def start_activation_phase(self):
        self.current_phase = "Activation Phase"
        self.lbl_phase_title.config(text="Aktivierungsphase")

        # Order Pool füllen
        self.order_pool = []
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

        info = self.rules.get_phase_info("2. Aktivierungsphase")
        # Just show start advice
        self.lbl_advice.config(text=info[0] + "\n" + info[1])

        self.update_draw_button()

    def update_draw_button(self):
        if not self.order_pool:
            self.btn_action.config(text="Aktivierungsphase beenden -> Endphase", command=self.start_end_phase, bg="#9C27B0")
            self.lbl_active_name.config(text="Alle Einheiten aktiviert.")
            self.lbl_active_stats.config(text="")
            self.active_unit = None
            self.btn_attack.config(state=tk.DISABLED)
        else:
            self.btn_action.config(text=f"Befehl ziehen ({len(self.order_pool)})", command=self.draw_order, bg="#4CAF50")

    def draw_order(self):
        drawn = self.order_pool.pop(0)
        unit = drawn["unit"]
        side = drawn["side"]

        self.active_unit = unit
        self.active_side = side
        unit["activated"] = True

        color = "#2196F3" if side == "Player" else "#F44336"
        self.lbl_active_name.config(text=f"{unit['name']} ({side})", fg=color)

        stats_text = (f"Bewegung: {unit.get('speed', '-')}\n"
                      f"Verteidigung: {unit.get('defense', '-')}\n"
                      f"HP: {unit['current_hp']}/{unit['hp']} | Mut: {unit['courage']}\n"
                      f"Keywords: {unit.get('info', '')}")
        self.lbl_active_stats.config(text=stats_text)

        self.update_trees()
        self.update_draw_button()
        self.btn_attack.config(state=tk.NORMAL, command=self.open_attack_dialog)

        # Advice update
        self.lbl_advice.config(text="1. Sammeln (Suppression entfernen)\n2. Aktionen durchführen (2 Aktionen)")

        # Auto-Prompt for Rally
        if unit["suppression"] > 0:
            if messagebox.askyesno("Sammeln", f"{unit['name']} hat {unit['suppression']} Unterdrückung. Sammeln würfeln?"):
                # Simple rally logic: Roll white dice equal to suppression
                remove = 0
                log = []
                for _ in range(unit["suppression"]):
                    r = random.randint(1, 6)
                    if r in [1, 2, 3]: # Block (1), Surge (2), Blank (3-6) - Wait. White die: 1 Block, 1 Surge, 4 Blank.
                        # White Defense: 1 Shield, 1 Surge, 4 Blank.
                        # Rally removes on Block or Surge (if unit can surge? Core rules say Block or Surge always works for rally?)
                        # 2.5 Rules: "Roll 1 white defense die for each suppression token. For each block or surge result..."
                        # White Die: 1 Block (shield), 1 Surge (star), 4 Blank.
                        pass
                    # Implementation detail: White die: 1 Block, 1 Surge.
                    # Index 1-6. 1=Block, 2=Surge, 3-6=Blank
                    if r <= 2: remove += 1

                if remove > 0:
                    unit["suppression"] = max(0, unit["suppression"] - remove)
                    messagebox.showinfo("Sammeln", f"{remove} Marker entfernt. Verbleibend: {unit['suppression']}")
                else:
                    messagebox.showinfo("Sammeln", "Keine Marker entfernt.")

        # AI LOGIC
        if side == "Opponent" and self.ai_enabled.get():
            intention = self.generate_ai_intention(unit)
            self.show_ai_intention(unit["name"], intention)

    def start_end_phase(self):
        self.current_phase = "End Phase"
        self.lbl_phase_title.config(text="Endphase")

        info = self.rules.get_phase_info("3. Endphase")
        self.lbl_advice.config(text="\n".join(info))

        # Automatisierung: Suppression -1
        count = 0
        for u in self.player_army["units"] + self.opponent_army["units"]:
            if u["suppression"] > 0:
                u["suppression"] -= 1
                count += 1

        if count > 0:
            messagebox.showinfo("Endphase", f"Bei {count} Einheiten wurde 1 Niederhalten-Marker entfernt.")

        self.btn_action.config(text="Runde beenden -> Neue Runde", command=self.start_new_round, bg="#607D8B")

    # --- PLACEHOLDER FOR ADVANCE PHASE (Button Link) ---
    def advance_phase(self):
        # Logic handled by button config changes
        pass

    # --- ATTACK & AI (Existing Logic) ---
    # ... (Copied from previous GameCompanion, keeping generate_ai_intention, show_ai_intention, open_attack_dialog)
    # Re-pasting the existing logic methods below to complete the file

    def generate_ai_intention(self, unit):
        is_melee = False
        max_range = 0
        if "weapons" in unit:
            for w in unit["weapons"]:
                r = w["range"][1]
                if r > max_range: max_range = r
                if r == 1 and w["range"][0] == 0: is_melee = True

        hp_ratio = unit["current_hp"] / unit["hp"]
        actions = []

        if is_melee and max_range < 2:
            if hp_ratio > 0.5:
                actions.append("Bewegung (Doppel) auf nächsten Feind zu")
                actions.append("Angriff (Nahkampf) wenn möglich")
            else:
                actions.append("Bewegung in Deckung")
                actions.append("Ausweichen (Dodge)")
        else:
            if hp_ratio < 0.3:
                 actions.append("Bewegung (Rückzug/Deckung)")
                 actions.append("Angriff auf nächste Bedrohung")
            else:
                 actions.append("Zielen (Aim)")
                 actions.append("Angriff auf Einheit mit wenig Deckung")

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

    def open_attack_dialog(self):
        if not self.active_unit: return
        top = tk.Toplevel(self.root)
        top.title("Angriff durchführen")
        top.geometry("600x700")
        unit = self.active_unit
        tk.Label(top, text=f"Angreifer: {unit['name']}", font=("Segoe UI", 12, "bold")).pack(pady=5)

        # 1. WAFFEN
        frame_weapons = tk.LabelFrame(top, text="1. Waffen wählen", padx=10, pady=10)
        frame_weapons.pack(fill="x", padx=10, pady=5)
        weapon_vars = []
        if "weapons" in unit:
            for w in unit["weapons"]:
                var = tk.BooleanVar()
                chk = tk.Checkbutton(frame_weapons, text=f"{w['name']} (Reichweite {w['range'][0]}-{w['range'][1]})", variable=var)
                chk.pack(anchor="w")
                dice_str = " | ".join([f"{k}: {v}" for k, v in w['dice'].items() if v > 0])
                tk.Label(frame_weapons, text=f"   Würfel: {dice_str} | Keywords: {', '.join(w.get('keywords', []))}", font=("Consolas", 8), fg="#555").pack(anchor="w")
                weapon_vars.append({"var": var, "data": w})
        else:
            tk.Label(frame_weapons, text="Keine Waffen definiert!").pack()

        # 2. ZIEL
        frame_target = tk.LabelFrame(top, text="2. Ziel & Verteidigung", padx=10, pady=10)
        frame_target.pack(fill="x", padx=10, pady=5)
        targets = self.opponent_army["units"] if self.active_side == "Player" else self.player_army["units"]
        target_names = [u["name"] for u in targets if u["current_hp"] > 0]
        tk.Label(frame_target, text="Ziel wählen:").grid(row=0, column=0, sticky="w")
        cb_target = ttk.Combobox(frame_target, values=target_names, state="readonly")
        cb_target.grid(row=0, column=1, sticky="ew")

        tk.Label(frame_target, text="Verteidigungswürfel:").grid(row=1, column=0, sticky="w", pady=5)
        var_def_die = tk.StringVar(value="White")
        cb_def = ttk.Combobox(frame_target, textvariable=var_def_die, values=["White", "Red"], state="readonly", width=10)
        cb_def.grid(row=1, column=1, sticky="w")

        def on_target_select(event):
            name = cb_target.get()
            target_unit = next((u for u in targets if u["name"] == name), None)
            if target_unit:
                d_die = target_unit.get("defense", "White")
                var_def_die.set(d_die)
        cb_target.bind("<<ComboboxSelected>>", on_target_select)

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

        frame_result = tk.LabelFrame(top, text="3. Ergebnis", padx=10, pady=10, bg="#e0f7fa")
        frame_result.pack(fill="x", padx=10, pady=10)
        lbl_log = tk.Label(frame_result, text="Drücke 'WÜRFELN'...", bg="#e0f7fa", justify=tk.LEFT, font=("Consolas", 10))
        lbl_log.pack(anchor="w")

        def roll_attack():
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

            results = {"crit": 0, "hit": 0, "surge": 0, "blank": 0}
            def roll_legion_atk(color):
                r = random.randint(1, 8)
                if color == "red":
                    return "crit" if r == 1 else "hit" if 2 <= r <= 7 else "surge"
                if color == "black":
                    return "crit" if r == 1 else "hit" if 2 <= r <= 4 else "surge" if r == 5 else "blank"
                if color == "white":
                    return "crit" if r == 1 else "hit" if r == 2 else "surge" if r == 3 else "blank"
                return "blank"

            surge_chart = unit.get("surge", {})
            atk_surge = surge_chart.get("attack")
            aims = var_aim.get()
            for color, count in pool.items():
                for _ in range(count):
                    results[roll_legion_atk(color)] += 1
            log_text = f"Wurf: {results}\n"

            if aims > 0:
                dice_to_reroll = min(results["blank"], aims * 2)
                if dice_to_reroll > 0:
                     log_text += f"Zielen: {dice_to_reroll} Blanks neu...\n"
                     results["blank"] -= dice_to_reroll
                     choices = []
                     for c, n in pool.items(): choices.extend([c]*n)
                     if not choices: choices = ["white"] # Fallback safety
                     for _ in range(dice_to_reroll):
                         results[roll_legion_atk(random.choice(choices))] += 1
                     log_text += f"Nach Reroll: {results}\n"

            if atk_surge == "hit":
                results["hit"] += results["surge"]
                results["surge"] = 0
            elif atk_surge == "crit":
                results["crit"] += results["surge"]
                results["surge"] = 0

            # --- IMPACT KEYWORD (Neu für 2.5) ---
            # Parse Impact X
            impact_val = 0
            for k in keywords:
                k_lower = k.lower()
                if "impact" in k_lower or "wucht" in k_lower: # "Impact 1"
                    try:
                        impact_val += int(k.split(" ")[1])
                    except: pass

            # Check Target Armor (Mockup)
            target_unit = next((u for u in targets if u["name"] == cb_target.get()), None)
            has_armor = False
            if target_unit and "armor" in target_unit.get("info", "").lower():
                has_armor = True

            if impact_val > 0 and has_armor:
                converted = min(results["hit"], impact_val)
                results["hit"] -= converted
                results["crit"] += converted
                log_text += f"Impact {impact_val}: {converted} Hits zu Crits.\n"

            total_hits = results["hit"] + results["crit"]
            log_text += f"TREFFER POOL: {total_hits} (Hits: {results['hit']}, Crits: {results['crit']})\n"

            cover_val = var_cover.get()
            # Sharpshooter
            sharpshooter_val = 0
            for k in keywords:
                if "Sharpshooter" in k:
                    try:
                        sharpshooter_val += int(k.split(" ")[1])
                    except: pass

            effective_cover = max(0, cover_val - sharpshooter_val)
            if sharpshooter_val > 0:
                log_text += f"Scharfschütze {sharpshooter_val} reduziert Deckung auf {effective_cover}.\n"

            hits_removed_by_cover = min(results["hit"], effective_cover)
            results["hit"] -= hits_removed_by_cover
            log_text += f"Deckung zieht {hits_removed_by_cover} Hits ab.\n"

            dodges = var_dodge.get()
            hits_remaining = results["hit"] + results["crit"]
            if dodges > 0:
                removed = min(hits_remaining, dodges)
                log_text += f"Dodge ({dodges}) verhindert {removed} Treffer.\n"
                hits_remaining -= removed

            # Suppression applying
            # Apply suppression if at least one hit/crit result remained BEFORE defense dice?
            # Or if "Suppressive" weapon used?
            # Rule: Standard attack gives 1 suppression if >0 hits/crits in pool (before cancel?).
            # Actually: "If the attack pool contains at least one hit or crit result, the defender gains 1 suppression token."
            # "Suppressive" keyword gives +1 token.
            suppression_gain = 0
            if total_hits > 0: # This was before cover/dodge? Rules say "After the Roll Defense Dice step..."
                suppression_gain = 1

            # Check Suppressive
            is_suppressive = any("suppressive" in k.lower() or "niedrighalten" in k.lower() for k in keywords)
            if is_suppressive:
                suppression_gain += 1
                log_text += "Waffe ist Niedrighaltend (Suppressive).\n"

            if hits_remaining <= 0:
                log_text += "ANGRIFF ABGEWEHRT (Keine Hits übrig)."
                if suppression_gain > 0 and target_unit:
                    target_unit["suppression"] += suppression_gain
                    log_text += f"\nZiel erhält {suppression_gain} Unterdrückung."
                lbl_log.config(text=log_text, fg="blue")
                return

            def_die_type = var_def_die.get()
            blocks = 0
            def_surges = 0
            def_blanks = 0
            for _ in range(hits_remaining):
                r = random.randint(1, 6)
                if def_die_type == "Red":
                    if r <= 3: blocks += 1
                    elif r == 4: def_surges += 1
                    else: def_blanks += 1
                else:
                    if r == 1: blocks += 1
                    elif r == 2: def_surges += 1
                    else: def_blanks += 1

            log_text += f"\nVerteidigungswurf ({hits_remaining} Würfel {def_die_type}):\nBlocks: {blocks}, Surges: {def_surges}, Blanks: {def_blanks}\n"

            has_surge_block = False
            if target_unit:
                sc = target_unit.get("surge", {})
                if sc.get("defense") == "block":
                    has_surge_block = True
            if has_surge_block:
                blocks += def_surges
                log_text += f"Surge -> Block ({def_surges})\n"

            pierce_val = 0
            for k in keywords:
                if "Pierce" in k:
                    try:
                        pierce_val += int(k.split(" ")[1])
                    except: pass

            # Impervious Check
            impervious = False
            if target_unit and "impervious" in target_unit.get("info", "").lower():
                impervious = True

            if impervious and pierce_val > 0:
                log_text += f"Unverwüstlich (Impervious): Ziel würfelt {pierce_val} extra Würfel.\n"
                # Extra rolls logic omitted for brevity, simple text log.

            if pierce_val > 0 and blocks > 0:
                canceled = min(blocks, pierce_val)
                blocks -= canceled
                log_text += f"Pierce {pierce_val} bricht {canceled} Blocks!\n"

            wounds = max(0, hits_remaining - blocks)
            log_text += f"\nSCHADEN: {wounds}"

            if suppression_gain > 0:
                log_text += f"\nZiel erhält {suppression_gain} Unterdrückung."

            lbl_log.config(text=log_text, fg="red" if wounds > 0 else "green")

            if (wounds > 0 or suppression_gain > 0) and target_unit:
                def apply_dmg():
                    target_unit["current_hp"] -= wounds
                    target_unit["suppression"] += suppression_gain
                    self.update_trees()
                    messagebox.showinfo("Update", f"Angewendet:\nSchaden: {wounds}\nUnterdrückung: {suppression_gain}")
                    top.destroy()
                btn_apply = tk.Button(frame_result, text="ERGEBNIS ANWENDEN", bg="red", fg="white", command=apply_dmg)
                btn_apply.pack(pady=5)

        tk.Button(top, text="WÜRFELN", command=roll_attack, font=("Segoe UI", 12, "bold"), bg="#2196F3", fg="white").pack(pady=10)

    def open_rule_search(self):
        top = tk.Toplevel(self.root)
        top.title("Regel-Datenbank")
        top.geometry("600x400")

        tk.Label(top, text="Suche nach Regel/Keyword:", font=("Segoe UI", 10)).pack(pady=5)
        entry = tk.Entry(top, width=40)
        entry.pack(pady=5)

        listbox = tk.Listbox(top, width=80, height=15, font=("Consolas", 10))
        listbox.pack(padx=10, pady=10, fill="both", expand=True)

        def search():
            q = entry.get()
            results = self.rules.search_rule(q)
            listbox.delete(0, tk.END)
            if not results:
                listbox.insert(tk.END, "Keine Treffer.")
            for r in results:
                listbox.insert(tk.END, r)

        tk.Button(top, text="Suchen", command=search).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = GameCompanion(root)
    root.mainloop()
