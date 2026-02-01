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
        self.rules = LegionRules
        self.root = root
        self.root.title("SW Legion: Game Companion & AI Simulator (v2.0 Rules)")
        self.root.geometry("1400x900")

        # Game State
        self.player_army = {"faction": "", "units": []}
        self.opponent_army = {"faction": "", "units": []}

        # New State Variables
        self.round_number = 0
        self.current_phase = "Setup" # Setup, Command, Activation, End
        self.player_hand = [] # List of Command Cards
        self.opponent_hand = []
        self.player_discard = []
        self.opponent_discard = []
        self.current_command_card = None # {"player": card, "opponent": card}
        self.priority_player = "Player" # or "Opponent" (Blue Player)

        # Order Pool: Liste von Tupeln (UnitObject, "Player" oder "Opponent")
        self.order_pool = []
        self.active_unit = None
        self.active_side = None # "Player" oder "Opponent"

        self.ai_enabled = tk.BooleanVar(value=True)

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
            command_cards = data.get("command_cards", [])

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
                self.player_army = {"faction": faction, "units": enriched_units, "command_cards": command_cards}
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
        for widget in self.frame_center.winfo_children():
            widget.destroy()

        # Start Setup Phase
        self.start_setup_phase()

    def start_setup_phase(self):
        self.current_phase = "Setup"
        tk.Label(self.frame_center, text="Phase: Spielvorbereitung", font=("Segoe UI", 20, "bold"), bg="#fafafa").pack(pady=20)

        info_frame = tk.Frame(self.frame_center, bg="#fafafa")
        info_frame.pack(pady=10)

        pre_loaded_cards = self.player_army.get("command_cards", [])

        if pre_loaded_cards and len(pre_loaded_cards) == 7:
            self.lbl_setup_status = tk.Label(info_frame, text="Kommandokarten aus Armeeliste geladen (7 Karten).", font=("Segoe UI", 12), fg="green", bg="#fafafa")
            self.lbl_setup_status.pack()
            self.player_hand = pre_loaded_cards

            # Optional: Allow edit?
            # For now, just proceed button
            self.btn_finish_setup = tk.Button(self.frame_center, text="Spiel starten", command=self.finish_setup, bg="#4CAF50", fg="white", font=("Segoe UI", 14, "bold"))
            self.btn_finish_setup.pack(pady=20)

        else:
            # Legacy / Manual
            self.lbl_setup_status = tk.Label(info_frame, text="Bitte wähle deine Kommandokarten (Hand von 7 Karten).", font=("Segoe UI", 12), bg="#fafafa")
            self.lbl_setup_status.pack()

            btn_deck = tk.Button(self.frame_center, text="Kommandokarten wählen", command=self.open_deck_builder, bg="#2196F3", fg="white", font=("Segoe UI", 12))
            btn_deck.pack(pady=20)

            self.btn_finish_setup = tk.Button(self.frame_center, text="Setup abschließen & Spiel starten", command=self.finish_setup, bg="#4CAF50", fg="white", font=("Segoe UI", 14, "bold"), state=tk.DISABLED)
            self.btn_finish_setup.pack(pady=20)

    def open_deck_builder(self):
        if not self.player_army["faction"]:
             messagebox.showwarning("Fehler", "Keine Spieler-Armee geladen.")
             return

        top = tk.Toplevel(self.root)
        top.title("Kommandokarten Hand (7 Karten)")
        top.geometry("1000x600")

        # Layout: Available (Left) -> Buttons -> Selected (Right)
        f_left = tk.LabelFrame(top, text="Verfügbare Karten")
        f_left.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        f_mid = tk.Frame(top)
        f_mid.pack(side="left", fill="y", padx=5)

        f_right = tk.LabelFrame(top, text="Gewählte Hand (0/7)")
        f_right.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Lists
        cols = ("Name", "Pips")
        tv_avail = ttk.Treeview(f_left, columns=cols, show="headings")
        tv_avail.heading("Name", text="Name")
        tv_avail.heading("Pips", text="•")
        tv_avail.column("Name", width=200)
        tv_avail.column("Pips", width=30, anchor="center")
        tv_avail.pack(fill="both", expand=True)

        tv_sel = ttk.Treeview(f_right, columns=cols, show="headings")
        tv_sel.heading("Name", text="Name")
        tv_sel.heading("Pips", text="•")
        tv_sel.column("Name", width=200)
        tv_sel.column("Pips", width=30, anchor="center")
        tv_sel.pack(fill="both", expand=True)

        # Load Cards
        all_cards = self.db.get_command_cards(self.player_army["faction"])
        # Only generic or units in army?
        # For simplicity, show all for faction + neutral.
        # Ideally we filter by units present (e.g. Vader cards only if Vader is in army).
        # We can try to filter:

        unit_names = [u["name"] for u in self.player_army["units"]]

        valid_pool = []
        for c in all_cards:
            # Check restriction? 'restricted_to_unit' isn't explicitly in CommandCards in catalog usually?
            # Actually catalog command cards have "restricted_to_unit": ["id"]
            # But my LegionData loader kept raw json for command cards.
            # Let's just show all for now to avoid blocking user.
            valid_pool.append(c)

        # Sort by pips
        valid_pool.sort(key=lambda x: x.get("pips", 0))

        for c in valid_pool:
            tv_avail.insert("", "end", values=(c["name"], c["pips"]), tags=(str(c),)) # Store full dict in tag? No, just match name
            # Hack: Store index or ID?
            # Let's just store name match.

        selected_cards = []

        def update_status():
            count = len(selected_cards)
            f_right.config(text=f"Gewählte Hand ({count}/7)")

            # Check constraints
            pips = [c.get("pips", 0) for c in selected_cards]
            c1 = pips.count(1)
            c2 = pips.count(2)
            c3 = pips.count(3)
            c4 = pips.count(4)

            valid = (c1 == 2 and c2 == 2 and c3 == 2 and c4 == 1)
            status_txt = f"1•: {c1}/2 | 2•: {c2}/2 | 3•: {c3}/2 | 4•: {c4}/1"

            if valid:
                lbl_status.config(text=f"GÜLTIG: {status_txt}", fg="green")
                btn_confirm.config(state=tk.NORMAL)
            else:
                lbl_status.config(text=f"UNGÜLTIG: {status_txt}", fg="red")
                btn_confirm.config(state=tk.DISABLED)

        def add_card():
            sel = tv_avail.focus()
            if not sel: return
            item = tv_avail.item(sel)
            name = item["values"][0]

            # Find card object
            card = next((c for c in valid_pool if c["name"] == name), None)
            if not card: return

            if len(selected_cards) >= 7: return
            if card in selected_cards: return # Unique

            selected_cards.append(card)
            tv_sel.insert("", "end", values=(card["name"], card["pips"]))
            update_status()

        def remove_card():
            sel = tv_sel.focus()
            if not sel: return
            item = tv_sel.item(sel)
            name = item["values"][0]

            card = next((c for c in selected_cards if c["name"] == name), None)
            if card:
                selected_cards.remove(card)
                tv_sel.delete(sel)
                update_status()

        def confirm():
            self.player_hand = selected_cards
            self.lbl_setup_status.config(text="Karten gewählt! Bereit zum Start.", fg="green")
            self.btn_finish_setup.config(state=tk.NORMAL)
            top.destroy()

        tk.Button(f_mid, text=">>", command=add_card).pack(pady=20)
        tk.Button(f_mid, text="<<", command=remove_card).pack(pady=20)

        lbl_status = tk.Label(top, text="...", font=("Segoe UI", 10, "bold"))
        lbl_status.pack(pady=10)

        btn_confirm = tk.Button(top, text="Speichern", command=confirm, state=tk.DISABLED, bg="#4CAF50", fg="white")
        btn_confirm.pack(pady=10)

        update_status()

    def generate_ai_deck(self):
        faction = self.opponent_army["faction"]
        all_cards = self.db.get_command_cards(faction)

        # Simple Logic: Try to fulfill 2/2/2/1 requirement
        c1 = [c for c in all_cards if c.get("pips") == 1]
        c2 = [c for c in all_cards if c.get("pips") == 2]
        c3 = [c for c in all_cards if c.get("pips") == 3]
        c4 = [c for c in all_cards if c.get("pips") == 4]

        hand = []
        # Random sample if enough, else take all
        hand.extend(random.sample(c1, min(len(c1), 2)))
        hand.extend(random.sample(c2, min(len(c2), 2)))
        hand.extend(random.sample(c3, min(len(c3), 2)))
        hand.extend(random.sample(c4, min(len(c4), 1)))

        # If not 7 (e.g. missing cards in DB), fill with placeholders or duplicates (not strict for AI)
        while len(hand) < 7:
            # Just add random cards to fill
             hand.append({"name": "AI Card", "pips": 1, "text": "Placeholder"})

        self.opponent_hand = hand

    def finish_setup(self):
        # AI Deck generation
        self.generate_ai_deck()

        # Start Round 1
        self.round_number = 1
        self.start_command_phase()

    def start_command_phase(self):
        self.current_phase = "Command"

        # Reset units for the round
        for u in self.player_army["units"] + self.opponent_army["units"]:
            u["activated"] = False
            u["order_token"] = False

        # UI
        for widget in self.frame_center.winfo_children(): widget.destroy()

        tk.Label(self.frame_center, text=f"RUNDE {self.round_number}: Kommandophase", font=("Segoe UI", 16, "bold")).pack(pady=10)

        # 1. Select Card
        tk.Label(self.frame_center, text="Wähle deine Kommandokarte:", font=("Segoe UI", 12)).pack()

        frame_cards = tk.Frame(self.frame_center)
        frame_cards.pack(pady=10)

        self.var_selected_card_name = tk.StringVar()

        if not self.player_hand:
             # Fallback if hand empty (shouldn't happen with Standing Orders unless played)
             # Return Standing Orders to hand if played?
             # Standing Orders is typically returned.
             # For now, if empty, recover discarded Standing Orders?
             pass

        for card in self.player_hand:
            btn = tk.Radiobutton(frame_cards, text=f"{card['name']} ({card['pips']}•)", variable=self.var_selected_card_name, value=card["name"], indicatoron=0, width=40, padx=20, pady=5, selectcolor="#bbdefb")
            btn.pack(pady=2, fill="x")

        btn_play = tk.Button(self.frame_center, text="Karte Spielen", command=self.resolve_command_cards, bg="#2196F3", fg="white", font=("Segoe UI", 12, "bold"))
        btn_play.pack(pady=20)

    def resolve_command_cards(self):
        p_card_name = self.var_selected_card_name.get()
        if not p_card_name:
            messagebox.showwarning("Info", "Bitte wähle eine Karte.")
            return

        # Get objects
        p_card = next(c for c in self.player_hand if c["name"] == p_card_name)

        # AI Select
        if self.opponent_hand:
            o_card = random.choice(self.opponent_hand)
        else:
            o_card = {"name": "Standing Orders", "pips": 4, "text": "-"}

        # Move to discard
        self.player_hand.remove(p_card)
        self.player_discard.append(p_card)
        if o_card in self.opponent_hand:
            self.opponent_hand.remove(o_card)
            self.opponent_discard.append(o_card)

        # Handle "Standing Orders" return logic (always returns to hand at end of phase, but let's simplify: it's in discard until recovered or special rule. Actually Standing Orders returns immediately? No, 'At end of Command Phase'. We'll handle cleanup later.)

        self.current_command_card = {"player": p_card, "opponent": o_card}

        # Determine Priority
        p_pips = p_card.get("pips", 4)
        o_pips = o_card.get("pips", 4)

        if p_pips < o_pips:
            self.priority_player = "Player"
            msg = "Spieler hat Priorität!"
        elif o_pips < p_pips:
            self.priority_player = "Opponent"
            msg = "Gegner hat Priorität!"
        else:
            # Tie: Roll red die? Random for now.
            roll = random.choice(["Player", "Opponent"])
            self.priority_player = roll
            msg = f"Gleichstand! {('Spieler' if roll == 'Player' else 'Gegner')} gewinnt den Wurf."

        # Show Result UI
        for widget in self.frame_center.winfo_children(): widget.destroy()

        tk.Label(self.frame_center, text=f"RUNDE {self.round_number}: Kommandokarten", font=("Segoe UI", 16, "bold")).pack(pady=10)

        f_res = tk.Frame(self.frame_center)
        f_res.pack(fill="x", pady=10)

        tk.Label(f_res, text="Spieler", fg="blue", font=("Segoe UI", 12, "bold")).pack(side="left", expand=True)
        tk.Label(f_res, text="Gegner", fg="red", font=("Segoe UI", 12, "bold")).pack(side="right", expand=True)

        f_cards = tk.Frame(self.frame_center)
        f_cards.pack(fill="x")

        # Player Card
        f_p = tk.Frame(f_cards, bg="#e3f2fd", relief="ridge", bd=2, width=250, height=100)
        f_p.pack_propagate(0)
        f_p.pack(side="left", padx=20)
        tk.Label(f_p, text=p_card['name'], bg="#e3f2fd", font=("bold")).pack(pady=5)
        tk.Label(f_p, text=f"{p_card.get('pips')} Pips", bg="#e3f2fd").pack()
        tk.Message(f_p, text=p_card.get('text', '')[:100]+"...", bg="#e3f2fd", width=230).pack()

        # Opponent Card
        f_o = tk.Frame(f_cards, bg="#ffebee", relief="ridge", bd=2, width=250, height=100)
        f_o.pack_propagate(0)
        f_o.pack(side="right", padx=20)
        tk.Label(f_o, text=o_card['name'], bg="#ffebee", font=("bold")).pack(pady=5)
        tk.Label(f_o, text=f"{o_card.get('pips')} Pips", bg="#ffebee").pack()
        tk.Message(f_o, text=o_card.get('text', '')[:100]+"...", bg="#ffebee", width=230).pack()

        tk.Label(self.frame_center, text=msg, font=("Segoe UI", 14, "bold"), fg="#4CAF50").pack(pady=20)

        tk.Button(self.frame_center, text="Befehle erteilen >", command=self.issue_orders_ui, bg="#FF9800", fg="white", font=("Segoe UI", 12)).pack(pady=10)

    def issue_orders_ui(self):
        for widget in self.frame_center.winfo_children(): widget.destroy()

        tk.Label(self.frame_center, text="Befehle erteilen", font=("Segoe UI", 16, "bold")).pack(pady=10)

        card_text = self.current_command_card["player"].get("text", "")
        tk.Label(self.frame_center, text=f"Kartentext: {card_text}", wraplength=500, justify="center").pack(pady=5)

        tk.Label(self.frame_center, text="Wähle Einheiten, die einen offenen Befehl erhalten:", font=("Segoe UI", 10)).pack(pady=5)

        # Checkbox List for Player Units
        self.order_vars = []

        frame_list = tk.Frame(self.frame_center)
        frame_list.pack(fill="both", expand=True, padx=20)

        canvas = tk.Canvas(frame_list)
        sb = tk.Scrollbar(frame_list, orient="vertical", command=canvas.yview)
        scroll_f = tk.Frame(canvas)

        scroll_f.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scroll_f, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)

        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        for u in self.player_army["units"]:
            if u["current_hp"] <= 0: continue
            var = tk.BooleanVar()
            c = tk.Checkbutton(scroll_f, text=f"{u['name']} ({u['rank']})", variable=var, anchor="w")
            c.pack(fill="x", padx=5, pady=2)
            self.order_vars.append({"unit": u, "var": var})

        tk.Button(self.frame_center, text="Bestätigen & Aktivierungsphase starten", command=self.finalize_command_phase, bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold")).pack(pady=10)

    def finalize_command_phase(self):
        # 1. Apply Player Orders
        count = 0
        for item in self.order_vars:
            if item["var"].get():
                item["unit"]["order_token"] = True
                count += 1

        # 2. Apply AI Orders (Simple Logic)
        # Based on Pips: 1->1, 2->2, 3->3, 4->1
        pips = self.current_command_card["opponent"].get("pips", 4)
        ai_orders_count = 3 if pips == 3 else (2 if pips == 2 else 1)

        # AI prioritizes Commander/Operative then Heavy then Special then Corps
        ai_units = [u for u in self.opponent_army["units"] if u["current_hp"] > 0]
        # Sort by rank priority (Commander=1...)
        rank_prio = {"Commander": 1, "Operative": 1, "Heavy": 2, "Special Forces": 3, "Support": 4, "Corps": 5}
        ai_units.sort(key=lambda x: rank_prio.get(x.get("rank"), 99))

        for i in range(min(len(ai_units), ai_orders_count)):
            ai_units[i]["order_token"] = True

        self.create_order_pool()
        self.start_activation_phase()

    def create_order_pool(self):
        self.order_pool = []
        # Add units WITHOUT order token to pool
        for u in self.player_army["units"]:
            if u["current_hp"] > 0 and not u.get("order_token"):
                self.order_pool.append({"unit": u, "side": "Player"})

        for u in self.opponent_army["units"]:
            if u["current_hp"] > 0 and not u.get("order_token"):
                self.order_pool.append({"unit": u, "side": "Opponent"})

        random.shuffle(self.order_pool)
        self.update_trees()

    def start_activation_phase(self):
        self.current_phase = "Activation"
        self.active_turn_player = self.priority_player
        self.start_turn()

    def start_turn(self):
        # UI Refresh
        for widget in self.frame_center.winfo_children(): widget.destroy()

        tk.Label(self.frame_center, text=f"RUNDE {self.round_number}: Aktivierungsphase", font=("Segoe UI", 16, "bold")).pack(pady=10)

        turn_color = "#2196F3" if self.active_turn_player == "Player" else "#F44336"
        turn_text = "SPIELER AM ZUG" if self.active_turn_player == "Player" else "GEGNER (AI) AM ZUG"
        tk.Label(self.frame_center, text=turn_text, font=("Segoe UI", 20, "bold"), fg=turn_color).pack(pady=10)

        # Info Box
        face_up_p = sum(1 for u in self.player_army['units'] if u.get('order_token') and not u.get('activated'))
        face_up_o = sum(1 for u in self.opponent_army['units'] if u.get('order_token') and not u.get('activated'))
        pool_count = len(self.order_pool)

        tk.Label(self.frame_center, text=f"Pool: {pool_count} | Offene Befehle: P={face_up_p}, G={face_up_o}", bg="#eee", padx=10).pack(pady=5)

        # Actions
        # Check if Human (Player) OR AI is disabled (Human Opponent)
        is_human_turn = (self.active_turn_player == "Player") or (not self.ai_enabled.get())

        if is_human_turn:
            turn_label = "Spieler Optionen" if self.active_turn_player == "Player" else "Gegner (Manuell) Optionen"

            # Player Options: Activate Face-Up OR Draw
            f_acts = tk.Frame(self.frame_center)
            f_acts.pack(pady=20)

            tk.Label(f_acts, text=turn_label, font=("bold")).pack(pady=5)

            # Draw Button
            state_draw = tk.NORMAL if pool_count > 0 else tk.DISABLED

            # Decide which pool to draw from based on active turn player
            cmd_draw = self.player_draw_pool if self.active_turn_player == "Player" else self.opponent_draw_pool_manual

            tk.Button(f_acts, text="Vom Stapel ziehen (Zufall)", command=cmd_draw, bg="#FF9800", fg="white", font=("bold"), state=state_draw, width=25).pack(pady=5)

            # Face Up Buttons
            current_army = self.player_army if self.active_turn_player == "Player" else self.opponent_army
            face_up_count = face_up_p if self.active_turn_player == "Player" else face_up_o

            if face_up_count > 0:
                tk.Label(f_acts, text="--- ODER Wähle Einheit (Offener Befehl) ---").pack(pady=10)
                for u in current_army["units"]:
                    if u.get("order_token") and not u.get("activated"):
                        tk.Button(f_acts, text=f"Aktiviere: {u['name']}", command=lambda unit=u: self.activate_unit(unit, self.active_turn_player)).pack(fill="x", pady=2)

            # Pass Button (Optional, not strictly checking count diff here for simplicity)
            tk.Button(f_acts, text="Passen (Runde beenden / Nächster)", command=self.pass_turn, bg="#9E9E9E", fg="white").pack(pady=20)

        else:
            # AI Turn
            tk.Label(self.frame_center, text="AI denkt nach...", font=("italic")).pack(pady=20)
            self.root.after(1000, self.ai_take_turn)

    def player_draw_pool(self):
        # Filter pool for player
        player_tokens = [t for t in self.order_pool if t["side"] == "Player"]
        if not player_tokens:
            messagebox.showinfo("Info", "Keine Befehlsmarker im Pool.")
            return

        # Draw one
        token = player_tokens[0] # They are shuffled
        self.order_pool.remove(token) # Remove from main list

        self.activate_unit(token["unit"], "Player")

    def opponent_draw_pool_manual(self):
        # Filter pool for opponent
        opp_tokens = [t for t in self.order_pool if t["side"] == "Opponent"]
        if not opp_tokens:
            messagebox.showinfo("Info", "Keine Befehlsmarker im Pool.")
            return

        token = opp_tokens[0]
        self.order_pool.remove(token)
        self.activate_unit(token["unit"], "Opponent")

    def ai_take_turn(self):
        # AI Logic
        # 1. Face Up?
        candidates_face_up = [u for u in self.opponent_army["units"] if u.get("order_token") and not u.get("activated") and u["current_hp"] > 0]

        unit_to_activate = None

        if candidates_face_up:
            # Pick highest rank
            # Sort logic...
            unit_to_activate = candidates_face_up[0] # Simplification
        else:
            # Draw from pool
            ai_tokens = [t for t in self.order_pool if t["side"] == "Opponent"]
            if ai_tokens:
                token = ai_tokens[0]
                self.order_pool.remove(token)
                unit_to_activate = token["unit"]

        if unit_to_activate:
            self.activate_unit(unit_to_activate, "Opponent")
        else:
            # No units left? Pass.
            self.pass_turn()

    def pass_turn(self):
        # Toggle Turn Player
        self.active_turn_player = "Opponent" if self.active_turn_player == "Player" else "Player"

        # Check if Round End (Both passed or no activations left?)
        # Simplified: If both pools empty and no face-ups?

        p_rem = any(not u.get("activated") and u["current_hp"] > 0 for u in self.player_army["units"])
        o_rem = any(not u.get("activated") and u["current_hp"] > 0 for u in self.opponent_army["units"])

        if not p_rem and not o_rem:
            self.end_phase()
        else:
            self.start_turn()

    def activate_unit(self, unit, side):
        self.active_unit = unit
        self.active_side = side
        self.actions_remaining = 2

        unit["activated"] = True
        unit["order_token"] = False # Flip down

        # UI for Activation
        for widget in self.frame_center.winfo_children(): widget.destroy()

        tk.Label(self.frame_center, text=f"AKTIV: {unit['name']}", font=("Segoe UI", 18, "bold"), fg=("blue" if side=="Player" else "red")).pack(pady=10)

        # 1. Start of Activation Effects (Placeholder)

        # 2. Rally Step
        self.perform_rally(unit)

        # 3. Actions UI
        self.update_actions_ui()

        # If AI, automate
        if side == "Opponent" and self.ai_enabled.get():
            self.root.after(1000, self.ai_perform_actions)

    def perform_rally(self, unit):
        suppression = unit.get("suppression", 0)
        courage = unit.get("courage", "-")

        # Remove suppression = Roll white dice equal to suppression
        if suppression > 0:
            removed = 0
            # Sim roll
            for _ in range(suppression):
                r = random.randint(1, 6)
                if r in [1, 2]: # Block or Surge (approx for White Defense Rally?)
                    # Rally rule: "Werfe 1 weißen Verteidigungswürfel für jeden Niederhalten-Marker. Für jede Abwehr oder Verteidigungsenergie entfernt sie 1."
                    # White Def: 1 Block, 1 Surge. Faces 1, 2. (Assuming 1-6 map: 1=Block, 2=Surge, 3-6=Blank)
                    removed += 1

            unit["suppression"] = max(0, suppression - removed)
            # Log?

        # Check Panic
        self.is_panicked = False
        if courage != "-":
            try:
                c_val = int(courage)
                if unit["suppression"] >= 2 * c_val:
                    self.is_panicked = True
            except: pass

        # Suppressed?
        self.is_suppressed = False
        if courage != "-":
             try:
                c_val = int(courage)
                if unit["suppression"] >= c_val:
                    self.is_suppressed = True
                    self.actions_remaining -= 1
             except: pass

    def update_actions_ui(self):
        # Clear specific frame or rebuild
        # Simplified: rebuild center bottom
        # ...

        f_status = tk.Frame(self.frame_center, bg="#eee", pady=5)
        f_status.pack(fill="x")

        tk.Label(f_status, text=f"Aktionen: {self.actions_remaining} | Suppression: {self.active_unit.get('suppression', 0)}", font=("bold"), bg="#eee").pack()
        if self.is_panicked:
            tk.Label(f_status, text="PANIK! Keine Aktionen.", fg="red", bg="#eee").pack()
        if self.is_suppressed:
            tk.Label(f_status, text="NIEDERGEHALTEN (-1 Aktion)", fg="orange", bg="#eee").pack()

        f_acts = tk.Frame(self.frame_center)
        f_acts.pack(pady=10)

        if self.active_side == "Player" and not self.is_panicked and self.actions_remaining > 0:
            btn_cfg = {"font": ("Segoe UI", 10), "width": 15, "bg": "#2196F3", "fg": "white"}

            tk.Button(f_acts, text="Bewegung", command=lambda: self.perform_action("Move"), **btn_cfg).grid(row=0, column=0, padx=5, pady=5)
            tk.Button(f_acts, text="Angriff", command=lambda: self.perform_action("Attack"), **btn_cfg).grid(row=0, column=1, padx=5, pady=5)
            tk.Button(f_acts, text="Zielen (Aim)", command=lambda: self.perform_action("Aim"), **btn_cfg).grid(row=1, column=0, padx=5, pady=5)
            tk.Button(f_acts, text="Ausweichen (Dodge)", command=lambda: self.perform_action("Dodge"), **btn_cfg).grid(row=1, column=1, padx=5, pady=5)
            tk.Button(f_acts, text="Bereitschaft", command=lambda: self.perform_action("Standby"), **btn_cfg).grid(row=2, column=0, padx=5, pady=5)
            tk.Button(f_acts, text="Erholung", command=lambda: self.perform_action("Recover"), **btn_cfg).grid(row=2, column=1, padx=5, pady=5)

            tk.Button(f_acts, text="Aktivierung Beenden", command=self.end_activation, bg="#F44336", fg="white", font=("bold")).grid(row=3, column=0, columnspan=2, pady=15)

        elif self.active_side == "Player" and (self.is_panicked or self.actions_remaining <= 0):
             tk.Button(f_acts, text="Aktivierung Beenden", command=self.end_activation, bg="#F44336", fg="white", font=("bold")).pack()

    def perform_action(self, action_type):
        if self.actions_remaining <= 0: return

        # Reduce actions immediately (except Attack which might cancel?)
        # For simplicity, reduce now.

        msg = f"Aktion: {action_type}"

        if action_type == "Move":
            self.open_move_dialog()
            return # Don't decrement yet, wait for dialog
        elif action_type == "Attack":
            self.open_attack_dialog()
            return # Don't decrement yet
        elif action_type == "Aim":
            self.active_unit["aim"] = self.active_unit.get("aim", 0) + 1
        elif action_type == "Dodge":
            self.active_unit["dodge"] = self.active_unit.get("dodge", 0) + 1
        elif action_type == "Standby":
            self.active_unit["standby"] = True
        elif action_type == "Recover":
            self.active_unit["suppression"] = 0
            # Ready cards...

        self.actions_remaining -= 1
        self.update_actions_ui()
        self.update_trees()

    def end_activation(self):
        # End effects
        if self.is_panicked:
            # Remove suppression = courage
            try:
                val = int(self.active_unit["courage"])
                self.active_unit["suppression"] = max(0, self.active_unit["suppression"] - val)
            except: pass

        self.active_unit = None
        self.pass_turn()

    def ai_perform_actions(self):
        # Generate instructions for the human player
        unit_name = self.active_unit["name"]
        instructions = []

        if self.is_panicked:
            instructions.append("1. PANIK: Einheit flieht (Sammeln von Mut).")
            instructions.append("2. Wirft alle Missionsziele ab.")
        else:
            # Simple AI Heuristic
            is_melee = False
            max_range = 0
            if "weapons" in self.active_unit:
                for w in self.active_unit["weapons"]:
                    if w["range"][1] > max_range: max_range = w["range"][1]
                    if w["range"][0] == 0: is_melee = True

            # Actions based on role
            if is_melee and max_range < 2:
                instructions.append("1. BEWEGUNG: Auf nächsten Feind zu (Doppelt).")
                instructions.append("   (Oder Angriff wenn in Reichweite).")
                instructions.append("2. ANGRIFF: Falls möglich (Nahkampf).")
            else:
                instructions.append("1. ZIELEN (AIM): Erhalte Zielmarker.")
                instructions.append(f"2. ANGRIFF: Auf Feind mit wenigster Deckung (Reichweite {max_range}).")

        # If simple Heuristic says Attack, we ask user for targets
        if not self.is_panicked and is_melee and max_range < 2:
             # Melee Attack Query
             self.ai_query_targets(self.active_unit, is_melee=True)
        elif not self.is_panicked and max_range >= 2:
             # Ranged Attack Query
             self.ai_query_targets(self.active_unit, is_melee=False)
        else:
            # Move only or Panic
            # Show Dialog
            msg = f"Einheit: {unit_name}\n\n" + "\n".join(instructions) + "\n\nBitte führe diese Aktionen auf dem Tisch aus."
            messagebox.showinfo("AI Zug Anweisung", msg)
            self.end_activation()

    def ai_query_targets(self, unit, is_melee):
        top = tk.Toplevel(self.root)
        top.title("AI Zielerfassung")
        top.geometry("500x600")

        tk.Label(top, text=f"AI Einheit: {unit['name']}", font=("bold", 12)).pack(pady=10)

        # Show Weapons
        tk.Label(top, text="Verfügbare Waffen:", font=("bold")).pack(anchor="w", padx=20)
        weapons_info = []
        best_weapon = None
        max_dice = 0

        if "weapons" in unit:
            for w in unit["weapons"]:
                # Filter melee/ranged based on intent
                r_min, r_max = w["range"]
                is_w_melee = (r_min == 0)

                # Check if weapon fits the AI intent
                if is_melee and not is_w_melee and r_min > 1: continue # Skip ranged weapons in melee intent? Or allow all?
                # Actually, in melee you can only use Melee (and Versatile).
                # Simplified: Just show all weapons and their ranges.

                dice_count = sum(w["dice"].values())
                if dice_count > max_dice:
                    max_dice = dice_count
                    best_weapon = w

                weapons_info.append(f"• {w['name']} (Reichweite {r_min}-{r_max})")

        for info in weapons_info:
            tk.Label(top, text=info, padx=20).pack(anchor="w")

        tk.Label(top, text="\nWelche Spieler-Einheiten sind in Reichweite & Sichtlinie?", font=("bold")).pack(pady=10)

        # Player Units Checkboxes
        target_vars = []
        frame_list = tk.Frame(top)
        frame_list.pack(fill="both", expand=True, padx=20)

        for p_unit in self.player_army["units"]:
            if p_unit["current_hp"] <= 0: continue

            var = tk.BooleanVar()
            c = tk.Checkbutton(frame_list, text=f"{p_unit['name']} (HP: {p_unit['current_hp']})", variable=var, anchor="w")
            c.pack(fill="x")
            target_vars.append({"unit": p_unit, "var": var})

        def confirm():
            valid_targets = [item["unit"] for item in target_vars if item["var"].get()]
            top.destroy()
            self.ai_decide_and_attack(valid_targets, best_weapon)

        tk.Button(top, text="Bestätigen", command=confirm, bg="#2196F3", fg="white", font=("bold")).pack(pady=20)

    def ai_decide_and_attack(self, valid_targets, best_weapon):
        if not valid_targets:
            messagebox.showinfo("AI Info", "Keine Ziele in Reichweite. AI führt Bewegung durch.")
            self.end_activation()
            return

        # Logic: Pick Lowest HP, then Random
        # Sort by current_hp
        valid_targets.sort(key=lambda u: u["current_hp"])

        # Pick first
        chosen_target = valid_targets[0]

        # Open Attack Dialog Pre-filled
        # We need to modify open_attack_dialog to accept params
        self.open_attack_dialog(pre_target=chosen_target["name"], pre_weapon=best_weapon["name"] if best_weapon else None)

    def open_move_dialog(self):
        top = tk.Toplevel(self.root)
        top.title("Bewegung")
        top.geometry("300x250")

        unit = self.active_unit
        max_speed = unit.get("speed", 2)

        tk.Label(top, text=f"Bewegung: {unit['name']}", font=("bold")).pack(pady=10)

        tk.Label(top, text="Gelände:").pack()
        var_terrain = tk.StringVar(value="Open")
        tk.Radiobutton(top, text="Offen", variable=var_terrain, value="Open").pack()
        tk.Radiobutton(top, text="Schwierig (-1 Speed)", variable=var_terrain, value="Difficult").pack()

        # New: Cover Status
        tk.Label(top, text="Endete die Bewegung in Deckung?").pack(pady=(10,0))
        var_cover_status = tk.IntVar(value=unit.get("cover_status", 0))
        tk.Radiobutton(top, text="Keine", variable=var_cover_status, value=0).pack()
        tk.Radiobutton(top, text="Leicht", variable=var_cover_status, value=1).pack()
        tk.Radiobutton(top, text="Schwer", variable=var_cover_status, value=2).pack()

        def confirm_move():
            final_speed = max_speed
            if var_terrain.get() == "Difficult":
                # Check Unhindered
                if "Ungehindert" in unit.get("info", "") or "Unhindered" in unit.get("info", ""):
                    pass
                else:
                    final_speed = max(1, final_speed - 1)

            # Save Cover Status
            unit["cover_status"] = var_cover_status.get()

            # Apply Keywords
            info_txt = unit.get("info", "")

            # Tactical -> Aim
            # "Taktisch X" or "Tactical X"
            tac_val = 0
            if "Taktisch" in info_txt:
                # Parse value? Simple check
                # Assume "Taktisch 1" usually.
                # Regex would be better but simple string check:
                parts = info_txt.split(",")
                for p in parts:
                    if "Taktisch" in p:
                        try: tac_val = int(p.strip().split(" ")[1])
                        except: tac_val = 1

            if tac_val > 0:
                unit["aim"] = unit.get("aim", 0) + tac_val
                messagebox.showinfo("Taktisch", f"Einheit erhält {tac_val} Zielmarker durch Bewegung.")

            # Agile -> Dodge
            agile_val = 0
            if "Agil" in info_txt or "Agile" in info_txt:
                 parts = info_txt.split(",")
                 for p in parts:
                    if "Agil" in p:
                        try: agile_val = int(p.strip().split(" ")[1])
                        except: agile_val = 1

            if agile_val > 0:
                unit["dodge"] = unit.get("dodge", 0) + agile_val
                messagebox.showinfo("Agil", f"Einheit erhält {agile_val} Ausweichmarker durch Bewegung.")

            self.actions_remaining -= 1
            self.update_actions_ui()
            self.update_trees()
            top.destroy()

        tk.Button(top, text=f"Bewegung durchführen (Max Speed {max_speed})", command=confirm_move, bg="#4CAF50", fg="white").pack(pady=20)

    def end_phase(self):
        self.current_phase = "End"
        for widget in self.frame_center.winfo_children(): widget.destroy()

        tk.Label(self.frame_center, text=f"Ende Runde {self.round_number}", font=("Segoe UI", 20, "bold")).pack(pady=20)

        # 1. Cleanup
        log = []
        all_units = self.player_army["units"] + self.opponent_army["units"]
        for u in all_units:
            # Remove Green Tokens
            if u.get("aim", 0) > 0: u["aim"] = 0
            if u.get("dodge", 0) > 0: u["dodge"] = 0
            if u.get("standby"): u["standby"] = False

            # Remove 1 Suppression
            if u.get("suppression", 0) > 0:
                u["suppression"] -= 1

            # Reset Activation
            u["activated"] = False
            u["order_token"] = False

        log.append("• Marker entfernt (Zielen, Ausweichen, Bereitschaft).")
        log.append("• 1 Niederhalten-Marker von jeder Einheit entfernt.")
        log.append("• Alle Einheiten bereitgemacht.")
        log.append("• Kommandokarten abgelegt.")

        tk.Label(self.frame_center, text="\n".join(log), bg="#e3f2fd", padx=20, pady=20, justify="left", font=("Segoe UI", 12)).pack(pady=10)

        self.update_trees()

        # Reset Active View
        self.lbl_active_name.config(text="-")
        self.lbl_active_stats.config(text="")
        self.active_unit = None

        # Next Round Button
        if self.round_number >= 6:
            tk.Label(self.frame_center, text="SPIELENDE (Runde 6 erreicht)", font=("Segoe UI", 24, "bold"), fg="red").pack(pady=20)
            tk.Button(self.frame_center, text="Spiel beenden", command=self.root.destroy, bg="#F44336", fg="white").pack()
        else:
            self.round_number += 1
            tk.Button(self.frame_center, text=f"Start Runde {self.round_number}", command=self.start_command_phase, bg="#4CAF50", fg="white", font=("Segoe UI", 14, "bold")).pack(pady=20)

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

    def open_attack_dialog(self, pre_target=None, pre_weapon=None):
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
                # Pre-select logic
                default_val = False
                if pre_weapon and w["name"] == pre_weapon:
                    default_val = True

                var = tk.BooleanVar(value=default_val)
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

        if pre_target:
            cb_target.set(pre_target)

        # Manuelle Overrides
        tk.Label(frame_target, text="Verteidigungswürfel:").grid(row=1, column=0, sticky="w", pady=5)
        var_def_die = tk.StringVar(value="White")
        cb_def = ttk.Combobox(frame_target, textvariable=var_def_die, values=["White", "Red"], state="readonly", width=10)
        cb_def.grid(row=1, column=1, sticky="w")

        # Deckung / Token Variables
        var_cover = tk.IntVar(value=0)

        # Auto-Fill Verteidigungswürfel bei Zielwahl
        def on_target_select(event):
            name = cb_target.get()
            target_unit = next((u for u in targets if u["name"] == name), None)
            if target_unit:
                d_die = target_unit.get("defense", "White")
                var_def_die.set(d_die)
                # Load Default Cover from unit state
                def_cover = target_unit.get("cover_status", 0)
                var_cover.set(def_cover)

        cb_target.bind("<<ComboboxSelected>>", on_target_select)

        # Deckung / Token UI
        tk.Label(frame_target, text="Deckung (Cover):").grid(row=2, column=0, sticky="w")
        tk.Radiobutton(frame_target, text="Keine", variable=var_cover, value=0).grid(row=2, column=1, sticky="w")
        tk.Radiobutton(frame_target, text="Leicht (1)", variable=var_cover, value=1).grid(row=2, column=2, sticky="w")
        tk.Radiobutton(frame_target, text="Schwer (2)", variable=var_cover, value=2).grid(row=2, column=3, sticky="w")

        tk.Label(frame_target, text="Ausweichen-Marker (Dodge):").grid(row=3, column=0, sticky="w")
        var_dodge = tk.IntVar(value=0)
        tk.Spinbox(frame_target, from_=0, to=10, textvariable=var_dodge, width=5).grid(row=3, column=1, sticky="w")

        tk.Label(frame_target, text="Zielen-Marker (Aim) [Angreifer]:").grid(row=4, column=0, sticky="w", pady=(10,0))
        var_aim = tk.IntVar(value=0)
        tk.Spinbox(frame_target, from_=0, to=10, textvariable=var_aim, width=5).grid(row=4, column=1, sticky="w", pady=(10,0))

        # Buttons Control Variable
        self.attack_rolled = False

        # 3. ERGEBNIS BEREICH
        frame_result = tk.LabelFrame(top, text="3. Ergebnis", padx=10, pady=10, bg="#e0f7fa")
        frame_result.pack(fill="x", padx=10, pady=10)

        lbl_log = tk.Label(frame_result, text="Drücke 'WÜRFELN'...", bg="#e0f7fa", justify=tk.LEFT, font=("Consolas", 10))
        lbl_log.pack(anchor="w")

        # LOGIK
        def roll_attack():
            # 1. Pool bilden
            pool = {"red": 0, "black": 0, "white": 0}
            selected_weapons = [w for w in weapon_vars if w["var"].get()]

            if not selected_weapons:
                messagebox.showwarning("Fehler", "Keine Waffe gewählt!")
                return

            # Keywords sammeln
            kw_map = {}

            # Unit Keywords
            for k in unit.get("info", "").split(","):
                k=k.strip()
                if not k: continue
                parts = k.split(" ")
                name = parts[0]
                val = 1
                if len(parts) > 1:
                    try: val = int(parts[1])
                    except: pass
                kw_map[name] = kw_map.get(name, 0) + val

            # Weapon Keywords
            for w in selected_weapons:
                wd = w["data"]
                for color, count in wd["dice"].items():
                    pool[color] += count
                for k in wd.get("keywords", []):
                    k=k.strip()
                    if not k: continue
                    parts = k.split(" ")
                    name = parts[0]
                    val = 1
                    if len(parts) > 1:
                        try: val = int(parts[1])
                        except: pass
                    kw_map[name] = kw_map.get(name, 0) + val

            # WÜRFELN (Angriff)
            results = {"crit": 0, "hit": 0, "surge": 0, "blank": 0}

            def roll_legion_atk(color):
                r = random.randint(1, 8)
                if color == "red":
                    if r == 1: return "crit"
                    if 2 <= r <= 7: return "hit"
                    return "surge"
                if color == "black":
                    if r == 1: return "crit"
                    if 2 <= r <= 4: return "hit"
                    if r == 5: return "surge"
                    return "blank"
                if color == "white":
                    if r == 1: return "crit"
                    if r == 2: return "hit"
                    if r == 3: return "surge"
                    return "blank"
                return "blank"

            # Roll initial pool
            for color, count in pool.items():
                for _ in range(count):
                    results[roll_legion_atk(color)] += 1

            log_text = f"Wurf: {results}\n"

            # --- KEYWORD LOGIC ---

            # PRECISE (Präzise) -> Aim Reroll Modifier
            aims = var_aim.get()
            precise_val = kw_map.get("Precise", 0) + kw_map.get("Präzise", 0)
            reroll_per_token = 2 + precise_val

            if aims > 0:
                dice_to_reroll = min(results["blank"] + results["surge"], aims * reroll_per_token) # Reroll blank and surge (if not surging)
                # Check surge conversion
                surge_chart = unit.get("surge", {})
                atk_surge = surge_chart.get("attack")

                # Don't reroll surge if we convert it
                if atk_surge:
                    dice_to_reroll = min(results["blank"], aims * reroll_per_token)

                if dice_to_reroll > 0:
                     log_text += f"Zielen (Präzise {precise_val}): {dice_to_reroll} Würfel neu...\n"
                     # Simple: Assume blanks are rerolled
                     results["blank"] = max(0, results["blank"] - dice_to_reroll)

                     choices = []
                     for c, n in pool.items(): choices.extend([c]*n)
                     if not choices: choices = ["white"] # Fallback

                     for _ in range(dice_to_reroll):
                         results[roll_legion_atk(random.choice(choices))] += 1
                     log_text += f"Nach Reroll: {results}\n"

            # CRITICAL (Kritisch) -> Surge to Crit
            crit_x = kw_map.get("Critical", 0) + kw_map.get("Kritisch", 0)
            if crit_x > 0 and results["surge"] > 0:
                converted = min(results["surge"], crit_x)
                results["surge"] -= converted
                results["crit"] += converted
                log_text += f"Kritisch {crit_x}: {converted} Surge -> Crit\n"

            # NATIVE SURGE
            surge_chart = unit.get("surge", {})
            atk_surge = surge_chart.get("attack")
            if results["surge"] > 0:
                if atk_surge == "hit":
                    results["hit"] += results["surge"]
                    log_text += f"Surge -> Hit ({results['surge']})\n"
                    results["surge"] = 0
                elif atk_surge == "crit":
                    results["crit"] += results["surge"]
                    log_text += f"Surge -> Crit ({results['surge']})\n"
                    results["surge"] = 0

            # IMPACT (Wucht) -> Hit to Crit if Armor
            impact_val = kw_map.get("Impact", 0) + kw_map.get("Wucht", 0)

            # Check Target Armor
            target_unit = next((u for u in targets if u["name"] == cb_target.get()), None)
            target_info = target_unit.get("info", "") if target_unit else ""
            has_armor = "Armor" in target_info or "Panzerung" in target_info

            if has_armor and impact_val > 0:
                converted = min(results["hit"], impact_val)
                results["hit"] -= converted
                results["crit"] += converted
                log_text += f"Wucht {impact_val} (vs Panzerung): {converted} Hit -> Crit\n"

            # --- DEFENSE START ---

            total_hits = results["hit"] + results["crit"]
            log_text += f"TREFFER POOL: {total_hits} (Hits: {results['hit']}, Crits: {results['crit']})\n"

            # SHARPSHOOTER (Scharfschütze) -> Cover Reduction
            ss_val = kw_map.get("Sharpshooter", 0) + kw_map.get("Scharfschütze", 0)

            # BLAST (Explosion) -> Ignore Cover
            blast_val = kw_map.get("Blast", 0) + kw_map.get("Explosion", 0)

            cover_val = var_cover.get()
            if blast_val > 0:
                cover_val = 0
                log_text += "Explosion: Deckung ignoriert.\n"
            else:
                if ss_val > 0 and cover_val > 0:
                    cover_val = max(0, cover_val - ss_val)
                    log_text += f"Scharfschütze {ss_val}: Deckung reduziert auf {cover_val}.\n"

            # APPLY COVER
            hits_removed_by_cover = min(results["hit"], cover_val) # Cover only hits
            results["hit"] -= hits_removed_by_cover
            if hits_removed_by_cover > 0:
                log_text += f"Deckung zieht {hits_removed_by_cover} Hits ab.\n"

            # DODGE
            dodges = var_dodge.get()
            # High Velocity check
            hv_val = kw_map.get("High Velocity", 0) + kw_map.get("Hochgeschwindigkeit", 0)
            if hv_val > 0:
                dodges = 0
                log_text += "Hochgeschwindigkeit: Ausweichen ignoriert.\n"

            hits_remaining = results["hit"] + results["crit"]
            if dodges > 0:
                removed = min(hits_remaining, dodges)
                log_text += f"Dodge ({dodges}) verhindert {removed} Treffer.\n"
                hits_remaining -= removed

            # Disable Roll Button
            self.attack_rolled = True
            btn_roll.config(state=tk.DISABLED)

            if hits_remaining <= 0:
                log_text += "ANGRIFF ABGEWEHRT (Keine Hits übrig)."
                lbl_log.config(text=log_text, fg="blue")
                # Even if 0 damage, we might want to apply "Attack Complete" state or Suppressive?
                # Check Suppressive logic below.
                # If 0 hits, standard suppression is 0, but keyword applies.
                # Fallthrough to apply button logic

            # ROLL DEFENSE
            if hits_remaining > 0:
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
                    else: # White
                        if r == 1: blocks += 1
                        elif r == 2: def_surges += 1
                        else: def_blanks += 1

                log_text += f"\nVerteidigungswurf ({hits_remaining} Würfel {def_die_type}):\nBlocks: {blocks}, Surges: {def_surges}, Blanks: {def_blanks}\n"

                # DEFENSE SURGE
                has_surge_block = False
                if target_unit:
                    sc = target_unit.get("surge", {})
                    if sc.get("defense") == "block":
                        has_surge_block = True

                if has_surge_block:
                    blocks += def_surges
                    log_text += f"Surge -> Block ({def_surges})\n"

                # PIERCE (Durchschlagen)
                pierce_val = kw_map.get("Pierce", 0) + kw_map.get("Durchschlagen", 0)

                # Immune: Pierce check
                immune_pierce = "Immune: Pierce" in target_info or "Immunität: Durchschlagen" in target_info

                if pierce_val > 0 and blocks > 0:
                    if immune_pierce:
                        log_text += "Ziel ist Immun gegen Durchschlagen.\n"
                    else:
                        canceled = min(blocks, pierce_val)
                        blocks -= canceled
                        log_text += f"Pierce {pierce_val} bricht {canceled} Blocks!\n"

                # FINAL WOUNDS
                wounds = max(0, hits_remaining - blocks)
                log_text += f"\nSCHADEN: {wounds}"
            else:
                wounds = 0

            # SUPPRESSION
            suppr_val = 0
            # Standard: If at least 1 Hit/Crit result
            if total_hits > 0:
                suppr_val += 1

            # Keyword: Suppressive
            if kw_map.get("Suppressive", 0) > 0 or kw_map.get("Niederhaltend", 0) > 0:
                suppr_val += 1

            if suppr_val > 0:
                log_text += f"\nNiederhalten: +{suppr_val}"

            lbl_log.config(text=log_text, fg="red" if wounds > 0 else ("orange" if suppr_val > 0 else "green"))

            # Apply Button
            if target_unit and (wounds > 0 or suppr_val > 0):
                def apply_result():
                    if wounds > 0:
                        target_unit["current_hp"] -= wounds
                    if suppr_val > 0:
                        target_unit["suppression"] = target_unit.get("suppression", 0) + suppr_val

                    self.update_trees()
                    messagebox.showinfo("Update", f"{target_unit['name']}:\n-{wounds} HP\n+{suppr_val} Suppression")
                    top.destroy()

                btn_apply = tk.Button(frame_result, text="ERGEBNIS ANWENDEN", bg="red", fg="white", command=apply_result)
                btn_apply.pack(pady=5)
            elif self.attack_rolled:
                 # If rolled but no damage/suppression (e.g. all misses, no Suppressive), just close
                 tk.Button(frame_result, text="ANGRIFF BEENDEN (Kein Effekt)", command=top.destroy, bg="#ccc").pack(pady=5)

        btn_roll = tk.Button(top, text="WÜRFELN", command=roll_attack, font=("Segoe UI", 12, "bold"), bg="#2196F3", fg="white")
        btn_roll.pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = GameCompanion(root)
    root.mainloop()
