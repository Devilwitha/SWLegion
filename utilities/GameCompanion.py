import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import random
import os
import logging
import sys

# Import utilities modules with compatibility for both script and package modes
try:
    # Try relative imports first (when imported as part of utilities package)
    from .LegionData import LegionDatabase
    from .LegionRules import LegionRules
    from .LegionUtils import get_writable_path
    logging.info("GameCompanion: Using relative imports")
except ImportError:
    try:
        # Try package imports (when running with MainMenu)
        from utilities.LegionData import LegionDatabase
        from utilities.LegionRules import LegionRules
        from utilities.LegionUtils import get_writable_path
        logging.info("GameCompanion: Using package imports")
    except ImportError:
        # Fallback to absolute imports (when running as standalone script)
        from LegionData import LegionDatabase
        from LegionRules import LegionRules
        from LegionUtils import get_writable_path
        logging.info("GameCompanion: Using absolute imports")

# Try to import MusicPlayer
try:
    from .MusicPlayer import MusicPlayer
except ImportError:
    try:
        from utilities.MusicPlayer import MusicPlayer
    except ImportError:
        try:
            from MusicPlayer import MusicPlayer
        except ImportError:
            MusicPlayer = None
            logging.warning("GameCompanion: Could not import MusicPlayer")

from PIL import Image, ImageTk

class GameCompanion:
    def __init__(self, root, mission_file=None):
        self.db = LegionDatabase()
        self.rules = LegionRules
        self.root = root

        # Tooltip-System initialisieren
        self.tooltip_window = None
        self.current_tooltip_widget = None

        logging.info("GameCompanion initialized.")
        self.root.title("SW Legion: Game Companion & AI Simulator (v2.0 Rules)")
        self.root.geometry("1400x900")
        
        # Set window icon
        try:
            # Get resource path for executable
            if getattr(sys, 'frozen', False):
                # Running as executable
                base_path = os.path.dirname(sys.executable)
                icon_path = os.path.join(base_path, "bilder", "SW_legion_logo.png")
            else:
                # Running as script
                icon_path = "bilder/SW_legion_logo.png"
            
            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path)
                icon_img = icon_img.resize((32, 32), Image.Resampling.LANCZOS)
                self.icon_photo = ImageTk.PhotoImage(icon_img)
                self.root.iconphoto(True, self.icon_photo)
        except Exception as e:
            logging.warning(f"Could not load icon: {e}")
            pass

        # Game State
        self.player_army = {"faction": "", "units": []}
        self.opponent_army = {"faction": "", "units": []}
        self.mission_data = None  # Initialize mission_data

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
        
        # Auto-load mission if provided
        if mission_file:
            self.root.after(500, lambda: self.load_mission_from_file(mission_file))

    def setup_ui(self):
        # Top Menü Leiste
        top_frame = tk.Frame(self.root, bg="#333", pady=5)
        top_frame.pack(fill="x")

        tk.Label(top_frame, text="Spiel-Begleiter", fg="white", bg="#333", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=10)

        btn_mission = tk.Button(top_frame, text="LADE MISSION", bg="#4CAF50", fg="white", command=self.load_mission)
        btn_mission.pack(side=tk.LEFT, padx=20)

        self.btn_show_scenario = tk.Button(top_frame, text="SZENARIO INFO", bg="#FFC107", fg="black", command=self.show_scenario_popup, state=tk.DISABLED)
        self.btn_show_scenario.pack(side=tk.LEFT, padx=5)

        btn_load_p = tk.Button(top_frame, text="Lade Spieler-Armee", bg="#2196F3", fg="white", command=lambda: self.load_army(True))
        btn_load_p.pack(side=tk.LEFT, padx=20)

        btn_load_o = tk.Button(top_frame, text="Lade Gegner-Armee (AI)", bg="#F44336", fg="white", command=lambda: self.load_army(False))
        btn_load_o.pack(side=tk.RIGHT, padx=20)

        # AI Checkbox oben
        chk_ai = tk.Checkbutton(top_frame, text="AI Aktiv", variable=self.ai_enabled, bg="#333", fg="white", selectcolor="#555", font=("Segoe UI", 10))
        chk_ai.pack(side=tk.RIGHT, padx=5)

        # Punkte-Anzeige
        self.score_frame = tk.Frame(top_frame, bg="#333")
        self.score_frame.pack(side=tk.RIGHT, padx=20)
        
        self.player_score = 0
        self.opponent_score = 0
        self.lbl_score = tk.Label(self.score_frame, text="Spieler: 0 | Gegner: 0", 
                                 font=("Segoe UI", 12, "bold"), fg="yellow", bg="#333")
        self.lbl_score.pack()

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
        
        # Event-Handler für Einheit-Auswahl hinzufügen
        tree.bind("<<TreeviewSelect>>", lambda e: self.on_unit_select(tree, e))
        
        tree.pack(fill="both", expand=True)
        return tree

    def on_unit_select(self, tree, event):
        """Handler für Einheit-Auswahl - zeigt Effekte und Fähigkeiten an"""
        selection = tree.selection()
        if not selection:
            return
            
        # Ermittle welcher Tree ausgewählt wurde
        is_player_tree = (tree == self.tree_player)
        
        # Hole das Item und finde die entsprechende Einheit
        item_id = selection[0]
        item_values = tree.item(item_id, 'values')
        unit_name = item_values[0] if item_values else ""
        
        # Finde die Einheit in der entsprechenden Armee
        target_army = self.player_army if is_player_tree else self.opponent_army
        selected_unit = None
        
        for unit in target_army.get("units", []):
            if unit.get("name") == unit_name:
                selected_unit = unit
                break
                
        if selected_unit:
            self.show_unit_effects(selected_unit, is_player_tree)

    def show_unit_effects(self, unit, is_player):
        """Zeigt ein Fenster mit allen Effekten und Fähigkeiten der Einheit"""
        effects_window = tk.Toplevel(self.root)
        effects_window.title(f"Effekte: {unit.get('name', 'Unbekannt')}")
        effects_window.geometry("500x600")
        effects_window.resizable(True, True)
        
        # Scrollbarer Frame
        canvas = tk.Canvas(effects_window)
        scrollbar = ttk.Scrollbar(effects_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header mit Einheit-Info
        header_frame = tk.Frame(scrollable_frame, bg="#2196F3", pady=10)
        header_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(header_frame, text=unit.get('name', 'Unbekannt'), 
                font=("Arial", 16, "bold"), fg="white", bg="#2196F3").pack()
        
        side_text = "Spieler" if is_player else "Gegner (AI)"
        tk.Label(header_frame, text=f"Seite: {side_text}", 
                font=("Arial", 12), fg="white", bg="#2196F3").pack()
        
        # Basis-Stats Frame
        stats_frame = tk.LabelFrame(scrollable_frame, text="📊 Basis-Statistiken", font=("Arial", 12, "bold"))
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        stats_text = f"""
🎯 Geschwindigkeit: {unit.get('speed', 'N/A')}
❤️ Lebenspunkte: {unit.get('current_hp', 'N/A')}/{unit.get('hp', 'N/A')}
👥 Miniaturen: {unit.get('minis', 'N/A')}
🛡️ Deckung: {unit.get('cover', 'N/A')}
⚔️ Mut: {unit.get('courage', 'N/A')}
💨 Unterdrückung: {unit.get('suppression', 0)}
🔸 Aktiviert: {'Ja' if unit.get('activated', False) else 'Nein'}
        """
        
        tk.Label(stats_frame, text=stats_text, font=("Arial", 10), justify="left").pack(anchor="w", padx=10, pady=5)
        
        # Schlüsselwörter/Fähigkeiten Frame
        keywords_frame = tk.LabelFrame(scrollable_frame, text="⭐ Fähigkeiten & Schlüsselwörter", font=("Arial", 12, "bold"))
        keywords_frame.pack(fill="x", padx=10, pady=5)
        
        keywords = unit.get('keywords', [])
        if keywords:
            for keyword in keywords:
                keyword_text = f"• {keyword}"
                # Beschreibung für bekannte Schlüsselwörter hinzufügen
                desc = self.get_keyword_description(keyword)
                if desc:
                    keyword_text += f"\n  → {desc}"
                
                tk.Label(keywords_frame, text=keyword_text, font=("Arial", 10), 
                        justify="left", wraplength=450).pack(anchor="w", padx=10, pady=2)
        else:
            tk.Label(keywords_frame, text="Keine besonderen Fähigkeiten", 
                    font=("Arial", 10), style="italic").pack(anchor="w", padx=10, pady=5)
        
        # Waffen Frame
        weapons_frame = tk.LabelFrame(scrollable_frame, text="⚔️ Waffen & Angriffe", font=("Arial", 12, "bold"))
        weapons_frame.pack(fill="x", padx=10, pady=5)
        
        weapons = unit.get('weapons', [])
        if weapons:
            for weapon in weapons:
                weapon_name = weapon.get('name', 'Unbekannte Waffe')
                weapon_range = weapon.get('range', 'N/A')
                weapon_dice = weapon.get('dice', 'N/A')
                weapon_keywords = weapon.get('keywords', [])
                
                weapon_text = f"🔫 {weapon_name}\n"
                weapon_text += f"   Reichweite: {weapon_range}\n"
                weapon_text += f"   Würfel: {weapon_dice}\n"
                
                if weapon_keywords:
                    weapon_text += f"   Eigenschaften: {', '.join(weapon_keywords)}\n"
                    
                tk.Label(weapons_frame, text=weapon_text, font=("Arial", 10), 
                        justify="left", bg="#f5f5f5").pack(fill="x", padx=10, pady=3)
        else:
            tk.Label(weapons_frame, text="Keine Waffen verfügbar", 
                    font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
        
        # Ausrüstung/Upgrades Frame  
        upgrades_frame = tk.LabelFrame(scrollable_frame, text="🎒 Ausrüstung & Upgrades", font=("Arial", 12, "bold"))
        upgrades_frame.pack(fill="x", padx=10, pady=5)
        
        upgrades = unit.get('upgrades', [])
        if upgrades:
            for upgrade in upgrades:
                # Upgrade kann string "Name (Punkte)" oder dict sein
                if isinstance(upgrade, str):
                    upgrade_text = f"• {upgrade}"
                    # Versuche Effekt-Beschreibung zu finden
                    upgrade_name = upgrade.split(' (')[0] if '(' in upgrade else upgrade
                    desc = self.get_upgrade_description(upgrade_name)
                    if desc:
                        upgrade_text += f"\n  → {desc}"
                else:
                    upgrade_text = f"• {upgrade.get('name', 'Unbekannt')}"
                    if upgrade.get('effect'):
                        upgrade_text += f"\n  → {upgrade['effect']}"
                        
                tk.Label(upgrades_frame, text=upgrade_text, font=("Arial", 10), 
                        justify="left", wraplength=450).pack(anchor="w", padx=10, pady=2)
        else:
            tk.Label(upgrades_frame, text="Keine Ausrüstung ausgewählt", 
                    font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
        
        # Status-Effekte Frame
        status_frame = tk.LabelFrame(scrollable_frame, text="🎭 Aktuelle Status-Effekte", font=("Arial", 12, "bold"))
        status_frame.pack(fill="x", padx=10, pady=5)
        
        status_effects = []
        
        # Marker-basierte Effekte
        if unit.get('markers'):
            for marker_type, count in unit['markers'].items():
                if count > 0:
                    effect_desc = self.get_marker_effect_description(marker_type)
                    status_effects.append(f"• {marker_type} ({count}x): {effect_desc}")
        
        # Weitere Statuseffekte
        if unit.get('suppression', 0) > 0:
            suppression = unit['suppression']
            courage = unit.get('courage', 2)
            if suppression >= courage * 2:
                status_effects.append("• Panisch: Kann nicht angreifen, nur Rally oder Bewegen")
            elif suppression >= courage:
                status_effects.append("• Unterdrückt: -1 Angriffs-Würfel")
            else:
                status_effects.append(f"• Unterdrückung: {suppression} (Keine Auswirkung)")
                
        if unit.get('activated', False):
            status_effects.append("• Aktiviert: Hat diese Runde bereits gehandelt")
            
        if status_effects:
            for effect in status_effects:
                tk.Label(status_frame, text=effect, font=("Arial", 10), 
                        justify="left", wraplength=450).pack(anchor="w", padx=10, pady=2)
        else:
            tk.Label(status_frame, text="Keine aktiven Status-Effekte", 
                    font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
        
        # Schließen Button
        close_button = tk.Button(scrollable_frame, text="Schließen", 
                               command=effects_window.destroy, 
                               bg="#f44336", fg="white", font=("Arial", 12))
        close_button.pack(pady=20)
        
        # Pack scrolling components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Center window on parent
        effects_window.transient(self.root)
        effects_window.grab_set()

    def get_keyword_description(self, keyword):
        """Gibt Beschreibung für bekannte Schlüsselwörter zurück"""
        descriptions = {
            "Armor": "Reduziert Treffer um 1 (außer bei kritischen Treffern)",
            "Armor X": "Reduziert Treffer um X (außer bei kritischen Treffern)", 
            "Arsenal X": "Kann bis zu X verschiedene Waffen pro Angriff verwenden",
            "Charge": "+1 Angriffs-Würfel bei Nahkampf nach Bewegung",
            "Climbing Gear": "Kann vertikale Oberflächen überqueren",
            "Danger Sense X": "Kann Deckung ignorieren bis Reichweite X",
            "Deflect": "Kann Schüsse auf Nahbereich-Ziele umleiten",
            "Disciplined X": "Entfernt X Unterdrückungs-Token bei Rally",
            "Duelist": "Angriffs-Würfel können nicht durch Deckung reduziert werden",
            "Exemplar": "Andere Einheiten im Bereich erhalten +1 Mut",
            "Expert Climber": "Ignoriert Bewegungsstrafen durch Gelände",
            "Fast": "Kann 1 kostenlosen Speed-1-Zug nach Aktion ausführen",
            "Fire Support": "Kann Angriff einer anderen Einheit unterstützen", 
            "Guardian X": "Kann Deckungsschuss für Einheiten in Reichweite X geben",
            "Immune: Pierce": "Pierce-Angriffe ignorieren Armor nicht",
            "Immune: Range 1 Weapons": "Immun gegen Angriffe in Reichweite 1",
            "Impact X": "Ändert X Treffer in kritische Treffer gegen Fahrzeuge",
            "Jump X": "Kann über Gelände bis Höhe X springen",
            "Low Profile": "Kann Deckung für Einheiten hinter sich bieten",
            "Marksman": "Präzisionsschüsse: Kann Ziele hinter Deckung treffen",
            "Nimble": "Kann Ausweich-Aktion nach Bewegung durchführen",
            "Pierce X": "Angriffe ignorieren X Armor",
            "Precise X": "Kann bis zu X Angriffswürfel neu werfen",
            "Relentless": "Kann nach Rally sofort einen Speed-1-Zug machen",
            "Scout X": "Kann nach Aufstellung X Speed-1-Züge machen",
            "Sharpshooter X": "Reduziert Deckungs-Bonus um X",
            "Steady": "Kann Zielen-Aktion nach Angriff durchführen",
            "Tactical X": "Kann X Command-Cards bei Taktikphase ziehen",
            "Uncanny Luck X": "Kann X Verteidigungswürfel neu werfen",
            "Weak Point X": "Angriffe gegen Fahrzeuge erhalten Pierce X"
        }
        return descriptions.get(keyword, "")

    def get_upgrade_description(self, upgrade_name):
        """Gibt Beschreibung für bekannte Upgrades zurück"""
        descriptions = {
            "DLT-19D": "Reichweite 1-4, 4 Würfel, Pierce 1",
            "Z-6 Rotary Blaster": "Reichweite 1-3, 6 Würfel", 
            "HH-12 Stormtrooper": "Reichweite 1-4, 4 Würfel, Pierce 1, Cumbersome",
            "MPL-57 Ion Blaster": "Reichweite 1-2, 4 Würfel, Ion 1",
            "Emergency Stims": "1x pro Spiel: Stelle 2 HP wieder her",
            "Bacta Capsules": "1x pro Spiel: Stelle 1 HP wieder her",
            "Targeting Scopes": "+1 Präzisionswürfel bei Zielen-Aktion",
            "Grappling Hooks": "Erhalte Expert Climber",
            "Electrobinoculars": "Spotte-Aktion: Gib einer Einheit Aim-Token",
            "Recon Intel": "Scout 1 nach Aufstellung",
            "Comms Jammer": "Feindliche Einheiten in Reichweite 1 erhalten -1 auf Command-Würfe",
            "Long-Range Comlink": "Kann Kommando von jeder Reichweite erhalten",
            "Frag Grenades": "Bereich-Angriff, Reichweite 1",
            "Impact Grenades": "Bereich-Angriff, Impact 1",
            "Concussion Grenades": "Bereich-Angriff, Blast, Suppressive"
        }
        return descriptions.get(upgrade_name, "")

    def get_marker_effect_description(self, marker_type):
        """Gibt Beschreibung für Marker-Effekte zurück"""
        descriptions = {
            "aim": "🎯 +1 Angriffs-Würfel und kann Würfel neu werfen",
            "dodge": "🛡️ +1 Verteidigungs-Würfel und kann Würfel neu werfen", 
            "suppression": "💨 Bei Courage-Wert: -1 Angriff, bei 2x Courage: Panik",
            "standby": "⏸️ Kann Aktion als Reaktion auf Gegner-Bewegung ausführen",
            "immobilized": "🚫 Kann sich nicht bewegen",
            "poisoned": "☠️ Erleidet Schaden am Ende jeder Runde", 
            "wounded": "🩸 Reduzierte Kampffähigkeit",
            "vehicle_damage": "🔥 Fahrzeug-Schadenspunkt"
        }
        return descriptions.get(marker_type, "Unbekannter Effekt")

    def create_hover_tooltip(self, widget, text):
        """Fügt einem Widget einen Hover-Tooltip hinzu"""
        def on_enter(event):
            self.show_hover_tooltip(event, text)
        def on_leave(event):
            self.hide_hover_tooltip()
            
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
    def show_hover_tooltip(self, event, text):
        """Zeigt Hover-Tooltip an"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            
        self.tooltip_window = tk.Toplevel(self.root)
        self.tooltip_window.wm_overrideredirect(True)
        
        # Position relativ zur Maus
        x = event.x_root + 10
        y = event.y_root + 10
        self.tooltip_window.geometry(f"+{x}+{y}")
        
        # Tooltip-Text mit Hintergrund
        label = tk.Label(self.tooltip_window, text=text, 
                        background="#ffffe0", foreground="black",
                        font=("Arial", 9), justify="left",
                        wraplength=400, relief="solid", borderwidth=1,
                        padx=8, pady=5)
        label.pack()
        
    def hide_hover_tooltip(self):
        """Versteckt Hover-Tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def has_usable_equipment(self, unit):
        """Prüft ob die Einheit nutzbare Ausrüstung hat"""
        if not unit or not unit.get('upgrades'):
            return False
            
        usable_equipment = [
            "Emergency Stims", "Bacta Capsules", "Electrobinoculars",
            "Frag Grenades", "Impact Grenades", "Concussion Grenades",
            "Smoke Grenades", "Thermal Detonators", "Comms Jammer"
        ]
        
        for upgrade in unit.get('upgrades', []):
            upgrade_name = upgrade.split(' (')[0] if isinstance(upgrade, str) else upgrade.get('name', '')
            if any(eq in upgrade_name for eq in usable_equipment):
                return True
        return False

    def use_equipment(self):
        """Zeigt Dialog zur Ausrüstungsnutzung"""
        if not self.active_unit:
            return
            
        equipment_window = tk.Toplevel(self.root)
        equipment_window.title("Ausrüstung nutzen")
        equipment_window.geometry("400x300")
        
        tk.Label(equipment_window, text="Verfügbare Ausrüstung", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Finde nutzbare Ausrüstung
        usable_items = []
        for upgrade in self.active_unit.get('upgrades', []):
            upgrade_name = upgrade.split(' (')[0] if isinstance(upgrade, str) else upgrade.get('name', '')
            
            # Check if already used (simplified - would need tracking)
            usable_items.append(upgrade_name)
        
        for item in usable_items:
            btn = tk.Button(equipment_window, text=f"Nutze: {item}",
                          command=lambda i=item: self.activate_equipment(i),
                          font=("Arial", 10), width=25, pady=3)
            btn.pack(pady=2)
        
        tk.Button(equipment_window, text="Abbrechen", 
                 command=equipment_window.destroy,
                 bg="#f44336", fg="white").pack(pady=20)

    def activate_equipment(self, equipment_name):
        """Aktiviert ein Ausrüstungsgegenstand"""
        unit_name = self.active_unit.get("name", "Unbekannt")
        
        effects = {
            "Emergency Stims": "Stelle 2 HP wieder her",
            "Bacta Capsules": "Stelle 1 HP wieder her", 
            "Electrobinoculars": "Gib einer verbündeten Einheit einen Aim-Token",
            "Frag Grenades": "Bereich-Schaden in Reichweite 1",
            "Comms Jammer": "Störe feindliche Kommunikation"
        }
        
        effect = effects.get(equipment_name, "Unbekannter Effekt")
        
        messagebox.showinfo("Ausrüstung aktiviert", 
                          f"{unit_name} nutzt: {equipment_name}\n\nEffekt: {effect}")
        
        # Heile wenn Stims oder Bacta
        if "Stims" in equipment_name:
            current_hp = self.active_unit.get("current_hp", 0)
            max_hp = self.active_unit.get("hp", 0)
            self.active_unit["current_hp"] = min(max_hp, current_hp + 2)
        elif "Bacta" in equipment_name:
            current_hp = self.active_unit.get("current_hp", 0)
            max_hp = self.active_unit.get("hp", 0)
            self.active_unit["current_hp"] = min(max_hp, current_hp + 1)
        
        # Schließe Fenster
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel) and "Ausrüstung" in widget.title():
                widget.destroy()
                break

    def get_melee_targets(self):
        """Findet alle Einheiten in Nahkampf-Reichweite (simuliert)"""
        targets = []
        
        # Simuliere Ziele basierend auf Gegner-Armee
        enemy_army = self.opponent_army if self.active_side == "Player" else self.player_army
        
        for unit in enemy_army.get("units", []):
            if unit.get("current_hp", 0) > 0:  # Nur lebende Einheiten
                # Simuliere dass einige Einheiten in Reichweite sind
                if random.random() < 0.4:  # 40% Chance in Nahkampf-Reichweite
                    targets.append(unit.get("name", "Unbekannt"))
        
        return targets

    def execute_melee_attack(self, target_name):
        """Führt Nahkampf-Angriff aus"""
        if not self.active_unit:
            return
            
        attacker = self.active_unit
        attacker_name = attacker.get("name", "Unbekannt")
        attacker_minis = attacker.get("minis", 1)
        
        # Finde Ziel-Einheit
        enemy_army = self.opponent_army if self.active_side == "Player" else self.player_army
        target_unit = None
        
        for unit in enemy_army.get("units", []):
            if unit.get("name") == target_name:
                target_unit = unit
                break
        
        if not target_unit:
            messagebox.showerror("Fehler", "Ziel nicht gefunden!")
            return
            
        target_minis = target_unit.get("minis", 1)
        
        # Berechne Angriffs-Würfel (Basis = Anzahl Miniaturen)
        attack_dice = attacker_minis
        
        # Bonus wenn mehr Minis als Gegner
        if attacker_minis > target_minis:
            attack_dice += 1
            
        # Würfle für Angriff
        hits = 0
        for _ in range(attack_dice):
            if random.randint(1, 8) >= 4:  # 4+ zum Treffen
                hits += 1
        
        # Verteidigung
        defense_dice = target_minis
        blocks = 0
        for _ in range(defense_dice):
            if random.randint(1, 8) >= 5:  # 5+ zum Blocken  
                blocks += 1
        
        # Schaden berechnen
        damage = max(0, hits - blocks)
        
        # Schaden anwenden (vereinfacht)
        old_hp = target_unit.get("current_hp", 0)
        new_hp = max(0, old_hp - damage)
        target_unit["current_hp"] = new_hp
        
        # Figuren entfernen bei HP-Verlust
        if damage > 0:
            self.apply_figure_damage(target_unit, damage)
        
        # Zurückschlag (falls Ziel noch lebt)
        counter_damage = 0
        if new_hp > 0:
            counter_dice = target_unit.get("minis", 1)
            counter_hits = sum(1 for _ in range(counter_dice) if random.randint(1, 8) >= 5)
            counter_blocks = sum(1 for _ in range(attacker_minis) if random.randint(1, 8) >= 5)
            counter_damage = max(0, counter_hits - counter_blocks)
            
            if counter_damage > 0:
                attacker_old_hp = attacker.get("current_hp", 0)
                attacker["current_hp"] = max(0, attacker_old_hp - counter_damage)
                self.apply_figure_damage(attacker, counter_damage)
        
        # Ergebnis anzeigen
        result_text = f"Nahkampf: {attacker_name} vs {target_name}\n\n"
        result_text += f"Angriff: {attack_dice} Würfel → {hits} Treffer\n"
        result_text += f"Verteidigung: {defense_dice} Würfel → {blocks} Blocks\n"
        result_text += f"Schaden an {target_name}: {damage}\n"
        
        if counter_damage > 0:
            result_text += f"\nZurückschlag: {counter_damage} Schaden an {attacker_name}"
        
        messagebox.showinfo("Nahkampf-Ergebnis", result_text)
        
        # Trees aktualisieren
        self.update_tree(self.tree_player, self.player_army["units"])
        self.update_tree(self.tree_opponent, self.opponent_army["units"])

    def show_explosion_effect(self):
        """Zeigt Explosions-Effekt"""
        messagebox.showinfo("Explosion!", 
                          "BOOM! 💥\n\nExplosion verursacht Bereich-Schaden!\n(Details würden basierend auf Missionsziel implementiert)")

    def show_repair_effect(self):
        """Zeigt Reparatur-Effekt"""
        messagebox.showinfo("Reparatur", 
                          "🔧 Reparatur erfolgreich!\n\nObjekt/Fahrzeug wurde repariert.")

    def load_army(self, is_player):
        # Determine initial directory based on mission or base folder
        initial_dir = get_writable_path("Armeen")

        # Try to match faction from mission
        if self.mission_data:
            target_faction = self.mission_data.get("blue_faction") if is_player else self.mission_data.get("red_faction")
            if target_faction:
                # Check if folder exists
                path = os.path.join(initial_dir, target_faction)
                if os.path.exists(path):
                    initial_dir = path

        # Directory creation handled by get_writable_path

        file_path = filedialog.askopenfilename(initialdir=initial_dir, title="Armee laden", filetypes=[("JSON", "*.json")])
        if not file_path: return

        try:
            logging.info(f"Loading army from {file_path}")
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
                logging.info(f"Player army loaded: {faction} ({len(enriched_units)} units)")
            else:
                self.opponent_army = {"faction": faction, "units": enriched_units, "command_cards": command_cards}
                self.update_tree(self.tree_opponent, self.opponent_army["units"])
                logging.info(f"Opponent army loaded: {faction} ({len(enriched_units)} units)")

        except Exception as e:
            logging.error(f"Failed to load army: {e}")
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
            if u.get("activated"):
                status = "Aktiviert"
            elif u.get("order_token"):
                status = "Offener Befehl"
            else:
                status = "Bereit"
            
            # Add markers to status
            markers = []
            if u.get("aim", 0) > 0:
                markers.append(f"🎯{u['aim']}")
            if u.get("dodge", 0) > 0:
                markers.append(f"💨{u['dodge']}")
            if u.get("suppression", 0) > 0:
                markers.append(f"📉{u['suppression']}")
            if u.get("standby", False):
                markers.append("⏸️")
            
            # PANIC-Zustand anzeigen
            panic_state = u.get("panic_state", "")
            if panic_state == "retreat":
                markers.append("🏃 RÜCKZUG")
            elif panic_state == "suppressed":
                markers.append("😰 UNTERDRÜCKT")
            
            # Courage vs Suppression Check
            try:
                courage_value = u.get("courage", 1)
                if courage_value == "-" or courage_value == "" or courage_value is None:
                    courage = 1
                else:
                    courage = int(courage_value)
                suppression = int(u.get("suppression", 0))
                if suppression >= courage and not panic_state:
                    markers.append("💀 PANIC!")
            except (ValueError, TypeError):
                # Fallback wenn Courage nicht als Zahl verfügbar
                pass
            
            if markers:
                status += f" {' '.join(markers)}"
            
            minis = u.get("minis", 1)
            # Zeige eliminated Status
            if minis <= 0:
                status = "💀 ELIMINATED"
                tree.insert("", "end", values=(f"❌ {u['name']}", 0, "0/0", status))
            else:
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

    def load_mission(self):
        initial_dir = get_writable_path("Missions")

        file_path = filedialog.askopenfilename(initialdir=initial_dir, title="Mission laden", filetypes=[("JSON", "*.json")])
        if file_path:
            self.load_mission_from_file(file_path)

    def load_mission_from_file(self, file_path):
        try:
            logging.info(f"Loading mission from {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                self.mission_data = json.load(f)

            # Refresh Setup if in Setup Phase
            if self.current_phase == "Setup":
                for widget in self.frame_center.winfo_children(): widget.destroy()
                self.start_setup_phase()

            # Enable Scenario Button
            if self.mission_data.get("scenario_text"):
                self.btn_show_scenario.config(state=tk.NORMAL)
            
            # Start Music if enabled
            if self.mission_data.get("music", {}).get("enabled"):
                self.start_mission_music()

            logging.info("Mission loaded successfully.")
            # Only show message if called interactively (not really easy to detect, but OK)
            messagebox.showinfo("Erfolg", "Mission geladen!\nDie Musik startet (falls aktiviert).")

        except Exception as e:
            logging.error(f"Error loading mission: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Laden der Mission: {e}")

    def start_mission_music(self):
        """Starts music based on mission settings"""
        if not MusicPlayer:
            logging.warning("MusicPlayer not available - Import failed")
            return
            
        settings = self.mission_data.get("music", {})
        playlist_name = settings.get("playlist")
        enabled = settings.get("enabled", False)
        
        logging.info(f"Attempting to start music. Enabled: {enabled}, Playlist: {playlist_name}")
        
        if enabled and playlist_name:
            try:
                # Close existing music window if open
                if hasattr(self, 'music_window') and self.music_window:
                    try:
                        self.music_window.destroy()
                    except: pass

                # Open as Toplevel window
                self.music_window = tk.Toplevel(self.root)
                self.music_app = MusicPlayer(self.music_window, start_with_playlist=playlist_name)
                logging.info(f"Music player started with playlist: {playlist_name}")
            except Exception as e:
                logging.error(f"Error starting music: {e}")
                messagebox.showerror("Musik Fehler", f"Konnte Musik nicht starten: {e}")
        else:
            logging.info("Music not enabled or no playlist selected in mission data")

    def show_scenario_popup(self):
        if not self.mission_data or not self.mission_data.get("scenario_text"):
            return

        top = tk.Toplevel(self.root)
        top.title("Szenario Details")
        top.geometry("600x800")

        txt = tk.Text(top, wrap="word", font=("Segoe UI", 11), padx=10, pady=10)
        txt.pack(fill="both", expand=True)
        
        # Configure bold formatting tag
        txt.tag_configure("bold", font=("Segoe UI", 11, "bold"))
        txt.tag_configure("italic", font=("Segoe UI", 11, "italic"))
        
        # Parse and insert formatted text
        scenario_text = self.mission_data.get("scenario_text", "")
        self.insert_formatted_text(txt, scenario_text)
        
        txt.config(state=tk.DISABLED)

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

    def start_setup_phase(self):
        self.current_phase = "Setup"
        tk.Label(self.frame_center, text="Phase: Spielvorbereitung", font=("Segoe UI", 20, "bold"), bg="#fafafa").pack(pady=20)

        # Mission Info
        info_frame = tk.Frame(self.frame_center, bg="#e1f5fe", relief="ridge", bd=2, padx=10, pady=10)
        info_frame.pack(pady=10, fill="x", padx=20)

        if self.mission_data:
            m = self.mission_data
            rounds_text = f" ({m.get('rounds', 6)} Runden)" if m.get('rounds') else ""
            txt = (f"MISSION: {m.get('mission_type', '-')}{rounds_text}\n"
                   f"AUFSTELLUNG: {m.get('deployment', '-')}\n"
                   f"PUNKTE: {m.get('points', '-')}\n\n"
                   f"SPIELER (BLAU): {m.get('blue_faction', '-')}\n"
                   f"GEGNER (ROT): {m.get('red_faction', '-')}")
            tk.Label(info_frame, text=txt, font=("Consolas", 10), justify="left", bg="#e1f5fe").pack()

            if m.get("scenario_text"):
                tk.Button(info_frame, text="Vollständiges Szenario lesen", command=self.show_scenario_popup, bg="#FFC107").pack(anchor="e", pady=5)
        else:
            tk.Label(info_frame, text="Keine Mission geladen.\nNutze 'LADE MISSION' oben.", font=("italic"), bg="#e1f5fe").pack()
            tk.Button(info_frame, text="Mission laden", command=self.load_mission, bg="#2196F3", fg="white").pack(pady=5)

        # Deck Status
        deck_frame = tk.Frame(self.frame_center, bg="#fafafa")
        deck_frame.pack(pady=10)

        self.lbl_setup_status = tk.Label(deck_frame, text="Überprüfe Kommandokarten...", font=("Segoe UI", 12), bg="#fafafa")
        self.lbl_setup_status.pack()

        pre_loaded_cards = self.player_army.get("command_cards", [])

        # NUR fragen wenn KEINE Karten hinterlegt sind
        if pre_loaded_cards and len(pre_loaded_cards) >= 7:
            # Nehme die ersten 7 Karten falls mehr vorhanden
            self.player_hand = pre_loaded_cards[:7]
            self.lbl_setup_status.config(text=f"✅ Kommandokarten aus Armeeliste geladen ({len(self.player_hand)} Karten).", fg="green")

            # Ready Button
            self.btn_finish_setup = tk.Button(self.frame_center, text="Spiel starten", command=self.finish_setup, bg="#4CAF50", fg="white", font=("Segoe UI", 14, "bold"))
            self.btn_finish_setup.pack(pady=20)

        elif pre_loaded_cards and len(pre_loaded_cards) > 0:
            # Teilweise Karten vorhanden - nutze diese und fülle auf 7 auf
            missing_count = 7 - len(pre_loaded_cards)
            self.player_hand = pre_loaded_cards[:]
            
            # Fülle mit Standard-Karten auf
            standard_cards = ["Standing Orders", "Push", "Ambush", "Assault", "Coordinated Bombardment", "Master of Evil", "Return of the Jedi"]
            for card in standard_cards:
                if len(self.player_hand) >= 7:
                    break
                if card not in self.player_hand:
                    self.player_hand.append(card)
            
            # Kürze auf 7 falls mehr vorhanden
            self.player_hand = self.player_hand[:7]
            self.lbl_setup_status.config(text=f"✅ Karten aus Armeeliste vervollständigt ({len(self.player_hand)} Karten).", fg="green")
            
            # Ready Button
            self.btn_finish_setup = tk.Button(self.frame_center, text="Spiel starten", command=self.finish_setup, bg="#4CAF50", fg="white", font=("Segoe UI", 14, "bold"))
            self.btn_finish_setup.pack(pady=20)

        else:
            # KEINE Karten hinterlegt - frage den Spieler
            self.lbl_setup_status.config(text="❗ Keine Kommandokarten in Armeeliste gefunden. Bitte wählen.", fg="red")
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
        
        # Versuche zuerst gespeicherte Command Cards zu laden
        if self.opponent_army.get("command_cards"):
            self.opponent_hand = self.opponent_army["command_cards"].copy()
            self.opponent_discard = []
            logging.info(f"Loaded opponent command cards from army file: {len(self.opponent_hand)} cards")
            return
            
        # Fallback: AI-Deck generieren
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
            btn = tk.Radiobutton(frame_cards, text=f"{card['name']} ({card['pips']}•)", 
                               variable=self.var_selected_card_name, value=card["name"], 
                               indicatoron=0, width=40, padx=20, pady=5, selectcolor="#bbdefb")
            btn.pack(pady=2, fill="x")
            
            # Hover-Tooltip für Command Cards hinzufügen
            self.create_hover_tooltip(btn, self.format_command_card_tooltip(card))

        btn_play = tk.Button(self.frame_center, text="Karte Spielen", command=self.resolve_command_cards, bg="#2196F3", fg="white", font=("Segoe UI", 12, "bold"))
        btn_play.pack(pady=20)

    def resolve_command_cards(self):
        p_card_name = self.var_selected_card_name.get()
        if not p_card_name:
            messagebox.showwarning("Info", "Bitte wähle eine Karte.")
            return

        # Get objects
        p_card = next(c for c in self.player_hand if c["name"] == p_card_name)

        # Prüfe ob Multi-Target Card
        if self.is_multi_target_card(p_card):
            targets = self.select_multiple_targets(p_card['name'])
            if targets:
                self.apply_multi_target_effect(p_card, targets)

        # Opponent Karte wählen
        if self.ai_enabled.get():
            # AI Select
            if self.opponent_hand:
                o_card = random.choice(self.opponent_hand)
            else:
                o_card = {"name": "Standing Orders", "pips": 4, "text": "-"}
        else:
            # Manueller Opponent - Karte wählen lassen
            o_card = self.select_opponent_command_card()
            if not o_card:
                return

        # Prüfe auch Opponent Card für Multi-Target
        if self.is_multi_target_card(o_card):
            # Temporär aktive Seite auf Gegner setzen
            original_side = self.active_side
            self.active_side = "Opponent"
            targets = self.select_multiple_targets(o_card['name'])
            if targets:
                self.apply_multi_target_effect(o_card, targets)
            self.active_side = original_side

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
        # Tooltip cleanup
        if getattr(self, 'tooltip_window', None):
            self.tooltip_window.destroy()
            self.tooltip_window = None
            
        for widget in self.frame_center.winfo_children(): widget.destroy()

        tk.Label(self.frame_center, text=f"RUNDE {self.round_number}: Kommandokarten", font=("Segoe UI", 16, "bold")).pack(pady=10)
        
        # Grid Setup for Cards
        cards_frame = tk.Frame(self.frame_center)
        cards_frame.pack(fill="both", expand=True, padx=20)
        
        # --- Player Card ---
        p_frame = tk.LabelFrame(cards_frame, text="Deine Karte", font=("Segoe UI", 12, "bold"), fg="blue")
        p_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        tk.Label(p_frame, text=p_card.get('name', 'Unbekannt'), font=("Segoe UI", 14, "bold")).pack(pady=5)
        tk.Label(p_frame, text=f"{p_pips} Pips", font=("Segoe UI", 12)).pack()
        tk.Label(p_frame, text=p_card.get('text', '-'), wraplength=300, justify="left").pack(pady=10, padx=5)
        
        # --- Opponent Card ---
        o_frame = tk.LabelFrame(cards_frame, text="Gegner Karte", font=("Segoe UI", 12, "bold"), fg="red")
        o_frame.pack(side="right", fill="both", expand=True, padx=10)
        
        tk.Label(o_frame, text=o_card.get('name', 'Standing Orders'), font=("Segoe UI", 14, "bold")).pack(pady=5)
        tk.Label(o_frame, text=f"{o_pips} Pips", font=("Segoe UI", 12)).pack()
        tk.Label(o_frame, text=o_card.get('text', '-'), wraplength=300, justify="left").pack(pady=10, padx=5)
        
        # --- Result ---
        res_frame = tk.Frame(self.frame_center)
        res_frame.pack(fill="x", pady=20)
        
        result_color = "green" if self.priority_player == "Player" else "red"
        tk.Label(res_frame, text=msg, font=("Segoe UI", 18, "bold"), fg=result_color).pack()
        
        # --- Continue Button ---
        tk.Button(self.frame_center, text="Weiter zu Befehlen", 
                 bg="#4CAF50", fg="white", font=("Segoe UI", 14, "bold"),
                 command=self.issue_orders_ui).pack(pady=20)

    def is_multi_target_card(self, command_card):
        """Prüft ob Command Card mehrere Ziele betreffen kann"""
        if not command_card:
            return False
            
        card_text = command_card.get('text', '').lower()
        card_name = command_card.get('name', '').lower()
        
        # Suche nach Multi-Target Schlüsselwörtern
        multi_target_keywords = [
            'bis zu', 'until', 'all', 'alle', 'each', 'jede', 'jeden',
            'choose', 'wähle', 'select', 'multiple', 'mehrere',
            'friendly units', 'verbündete einheiten', 'up to'
        ]
        
        for keyword in multi_target_keywords:
            if keyword in card_text or keyword in card_name:
                return True
                
        return False

    def select_multiple_targets(self, card_name, max_targets=None):
        """Dialog zur Auswahl mehrerer Ziele für Command Cards"""
        if self.active_side == "Player":
            available_units = self.player_army.get('units', [])
            side_name = "Spieler"
        else:
            available_units = self.opponent_army.get('units', [])
            side_name = "Gegner"
            
        # Filter nur lebende Einheiten
        available_units = [unit for unit in available_units if unit.get('current_hp', 0) > 0]
        
        if not available_units:
            messagebox.showinfo("Keine Ziele", "Keine verfügbaren Einheiten zum Auswählen!")
            return []
            
        # Dialog erstellen
        selection_window = tk.Toplevel(self.root)
        selection_window.title(f"Wähle Ziele für {card_name}")
        selection_window.geometry("500x400")
        selection_window.grab_set()
        
        tk.Label(selection_window, text=f"Wähle Einheiten für Command Card: {card_name}", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        if max_targets:
            tk.Label(selection_window, text=f"Maximum {max_targets} Einheiten auswählen", 
                    font=("Arial", 10), fg="blue").pack()
        
        # Listbox mit Checkboxen
        frame = tk.Frame(selection_window)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollbare Liste
        list_frame = tk.Frame(frame)
        list_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Checkbox Variables
        selected_vars = []
        selected_units = []
        
        for i, unit in enumerate(available_units):
            var = tk.BooleanVar()
            selected_vars.append(var)
            
            unit_name = unit.get('name', f'Einheit {i+1}')
            unit_hp = f"{unit.get('current_hp', 0)}/{unit.get('hp', 0)}"
            
            chk = tk.Checkbutton(scrollable_frame, text=f"{unit_name} (HP: {unit_hp})", 
                               variable=var, font=("Arial", 10))
            chk.pack(anchor="w", padx=10, pady=2)
            
            # Funktion für max_targets Begrenzung
            if max_targets:
                def check_limit(v=var, idx=i):
                    if v.get():
                        selected_count = sum(1 for sv in selected_vars if sv.get())
                        if selected_count > max_targets:
                            v.set(False)
                            messagebox.showwarning("Limit erreicht", 
                                                 f"Maximal {max_targets} Einheiten können ausgewählt werden!")
                
                var.trace('w', lambda *args, v=var, idx=i: check_limit(v, idx))
        
        scrollable_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Buttons
        btn_frame = tk.Frame(selection_window)
        btn_frame.pack(pady=10)
        
        def confirm_selection():
            selected = []
            for i, var in enumerate(selected_vars):
                if var.get():
                    selected.append(available_units[i])
            
            if not selected:
                messagebox.showwarning("Keine Auswahl", "Mindestens eine Einheit muss ausgewählt werden!")
                return
                
            selected_units.extend(selected)
            selection_window.destroy()
        
        def cancel_selection():
            selection_window.destroy()
        
        tk.Button(btn_frame, text="✓ Bestätigen", bg="#4CAF50", fg="white", 
                 command=confirm_selection).pack(side="left", padx=10)
        tk.Button(btn_frame, text="✗ Abbrechen", bg="#f44336", fg="white", 
                 command=cancel_selection).pack(side="left", padx=10)
        
        # Warten auf Auswahl
        selection_window.wait_window()
        return selected_units

    def apply_multi_target_effect(self, command_card, selected_units):
        """Wendet Command Card Effekt auf mehrere Einheiten an"""
        if not command_card or not selected_units:
            return
            
        card_name = command_card.get('name', 'Unbekannt')
        effect_text = command_card.get('text', '')
        
        # Log der Anwendung
        log_text = f"Command Card '{card_name}' wird auf {len(selected_units)} Einheiten angewendet:\n\n"
        
        for unit in selected_units:
            unit_name = unit.get('name', 'Unbekannt')
            log_text += f"🎯 {unit_name}:\n"
            
            # Beispiel-Effekte (müssen je nach Card angepasst werden)
            if 'rally' in effect_text.lower() or 'unterdrückung' in effect_text.lower():
                # Entferne Unterdrückung
                current_suppression = unit.get('suppression', 0)
                if current_suppression > 0:
                    unit['suppression'] = max(0, current_suppression - 1)
                    log_text += f"  → Unterdrückung reduziert auf {unit['suppression']}\n"
                else:
                    log_text += f"  → Keine Unterdrückung vorhanden\n"
                    
            elif 'aim' in effect_text.lower() or 'ziel' in effect_text.lower():
                # Füge Aim-Token hinzu
                aim_tokens = unit.get('aim_tokens', 0)
                unit['aim_tokens'] = aim_tokens + 1
                log_text += f"  → Ziel-Token hinzugefügt (Total: {unit['aim_tokens']})\n"
                
            elif 'move' in effect_text.lower() or 'bewegen' in effect_text.lower():
                # Zusätzliche Bewegung
                unit['extra_move'] = unit.get('extra_move', 0) + 1
                log_text += f"  → Kann sich zusätzlich bewegen (Free Move: {unit['extra_move']})\n"
                
            elif 'heal' in effect_text.lower() or 'heilung' in effect_text.lower():
                # Heilung
                current_hp = unit.get('current_hp', 0)
                max_hp = unit.get('hp', 0)
                if current_hp < max_hp:
                    unit['current_hp'] = min(max_hp, current_hp + 1)
                    log_text += f"  → Geheilt auf {unit['current_hp']}/{max_hp} HP\n"
                else:
                    log_text += f"  → Bereits bei maximaler Gesundheit\n"
                    
            elif 'dodge' in effect_text.lower() or 'ausweichen' in effect_text.lower():
                # Dodge-Token hinzufügen
                dodge_tokens = unit.get('dodge_tokens', 0)
                unit['dodge_tokens'] = dodge_tokens + 1
                log_text += f"  → Ausweich-Token hinzugefügt (Total: {unit['dodge_tokens']})\n"
                
            else:
                log_text += f"  → Allgemeiner Effekt angewendet\n"
            
            log_text += "\n"
        
        # Zeige Ergebnis
        result_window = tk.Toplevel(self.root)
        result_window.title("Command Card Effekt")
        result_window.geometry("600x500")
        result_window.grab_set()
        
        tk.Label(result_window, text="Command Card Angewendet!", 
                font=("Arial", 14, "bold"), fg="green").pack(pady=10)
        
        # Scrollbarer Text
        text_frame = tk.Frame(result_window)
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        text_widget = tk.Text(text_frame, wrap="word", font=("Arial", 10))
        scrollbar_result = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar_result.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=scrollbar_result.set)
        
        text_widget.insert("1.0", log_text)
        text_widget.config(state="disabled")
        
        tk.Button(result_window, text="OK", command=result_window.destroy).pack(pady=10)
        
        # Update UI
        self.update_trees()

    def create_hover_tooltip(self, widget, text):
        """Erstellt ein Hover-Tooltip für ein Widget"""
        def show_tooltip(event):
            if self.tooltip_window:
                self.tooltip_window.destroy()
            
            x, y, _, _ = widget.bbox("insert") if hasattr(widget, 'bbox') else (0, 0, 0, 0)
            x += widget.winfo_rootx() + 20
            y += widget.winfo_rooty() + 20
            
            self.tooltip_window = tk.Toplevel(widget)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.geometry(f"+{x}+{y}")
            
            # Tooltip-Inhalt
            tooltip_frame = tk.Frame(self.tooltip_window, bg="lightyellow", relief="solid", borderwidth=1)
            tooltip_frame.pack()
            
            tooltip_label = tk.Label(tooltip_frame, text=text, bg="lightyellow", 
                                   font=("Arial", 9), wraplength=400, justify="left")
            tooltip_label.pack(padx=5, pady=2)
            
            self.current_tooltip_widget = widget

        def hide_tooltip(event):
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None
            self.current_tooltip_widget = None

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
        widget.bind("<ButtonPress>", hide_tooltip)  # Verstecke bei Klick

    def format_command_card_tooltip(self, card):
        """Formatiert Command Card Information für Tooltip"""
        if not card:
            return "Keine Karteninformation verfügbar"
        
        tooltip_text = f"📜 {card.get('name', 'Unbekannt')}\n"
        tooltip_text += f"🎯 Pips: {card.get('pips', 'N/A')}\n\n"
        
        # Regeltext
        card_text = card.get('text', '')
        if card_text and card_text != '-':
            tooltip_text += f"📖 Effekt:\n{card_text}\n\n"
        
        # Multi-Target Hinweis
        if self.is_multi_target_card(card):
            tooltip_text += "⚡ Diese Karte kann mehrere Ziele betreffen!"
        
        return tooltip_text

    def format_unit_tooltip(self, unit):
        """Formatiert Einheiten-Information für Tooltip"""
        if not unit:
            return "Keine Einheiteninformation verfügbar"
        
        tooltip_text = f"🎯 {unit.get('name', 'Unbekannt')}\n"
        tooltip_text += f"❤️ HP: {unit.get('current_hp', 0)}/{unit.get('hp', 0)}\n"
        tooltip_text += f"⚔️ Mut: {unit.get('courage', 'N/A')}\n"
        tooltip_text += f"🛡️ Deckung: {unit.get('cover', 'N/A')}\n"
        tooltip_text += f"🏃 Speed: {unit.get('speed', 'N/A')}\n"
        
        # Status-Effekte
        suppression = unit.get('suppression', 0)
        if suppression > 0:
            tooltip_text += f"💨 Unterdrückung: {suppression}\n"
        
        aim_tokens = unit.get('aim_tokens', 0)
        if aim_tokens > 0:
            tooltip_text += f"🎯 Ziel-Token: {aim_tokens}\n"
        
        dodge_tokens = unit.get('dodge_tokens', 0)
        if dodge_tokens > 0:
            tooltip_text += f"🛡️ Ausweich-Token: {dodge_tokens}\n"
        
        # Aktivierungsstatus
        if unit.get('activated', False):
            tooltip_text += "✅ Bereits aktiviert"
        else:
            tooltip_text += "⭕ Noch nicht aktiviert"
        
        return tooltip_text

    def format_upgrade_tooltip(self, upgrade):
        """Formatiert Ausrüstungs-Information für Tooltip"""
        if not upgrade:
            return "Keine Ausrüstungsinformation verfügbar"
        
        tooltip_text = f"🎒 {upgrade.get('name', 'Unbekannt')}\n"
        tooltip_text += f"💰 Kosten: {upgrade.get('points', 'N/A')} Punkte\n"
        tooltip_text += f"🔧 Slot: {upgrade.get('slot', 'N/A')}\n\n"
        
        # Regeltext
        upgrade_text = upgrade.get('text', '')
        if upgrade_text:
            tooltip_text += f"📖 Effekt:\n{upgrade_text}\n"
        
        # Schlüsselwörter
        keywords = upgrade.get('keywords', [])
        if keywords:
            tooltip_text += f"⭐ Keywords: {', '.join(keywords)}\n"
        
        return tooltip_text

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

    def select_opponent_command_card(self):
        """Lasse Spieler 2 eine Kommandokarte auswählen"""
        if not self.opponent_hand:
            return {"name": "Standing Orders", "pips": 4, "text": "-"}
        
        # Dialog für Kartenwahl
        card_dialog = tk.Toplevel(self.root)
        card_dialog.title("Spieler 2 - Kommandokarte wählen")
        card_dialog.geometry("400x500")
        card_dialog.transient(self.root)
        card_dialog.grab_set()
        
        selected_card = [None]  # Mutable container for result
        
        tk.Label(card_dialog, text="Spieler 2: Wähle deine Kommandokarte", 
                font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        var_opponent_card = tk.StringVar()
        
        for card in self.opponent_hand:
            btn = tk.Radiobutton(card_dialog, 
                text=f"{card['name']} ({card['pips']}•)\\n{card.get('text', '')[:50]}...",
                variable=var_opponent_card, value=card["name"],
                indicatoron=1, wraplength=350, justify="left")
            btn.pack(pady=5, padx=20, anchor="w")
        
        def confirm_selection():
            card_name = var_opponent_card.get()
            if not card_name:
                messagebox.showwarning("Auswahl", "Bitte wähle eine Karte!")
                return
            selected_card[0] = next(c for c in self.opponent_hand if c["name"] == card_name)
            card_dialog.destroy()
        
        tk.Button(card_dialog, text="Karte bestätigen", command=confirm_selection,
                 bg="#4CAF50", fg="white", font=("Segoe UI", 12)).pack(pady=20)
        
        # Wait for dialog to close
        card_dialog.wait_window()
        return selected_card[0]

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

        # 2. Apply Opponent Orders
        if self.ai_enabled.get():
            # AI Orders (Simple Logic)
            pips = self.current_command_card["opponent"].get("pips", 4)
            ai_orders_count = 3 if pips == 3 else (2 if pips == 2 else 1)

            # AI prioritizes Commander/Operative then Heavy then Special then Corps
            ai_units = [u for u in self.opponent_army["units"] if u["current_hp"] > 0]
            # Sort by rank priority (Commander=1...)
            rank_prio = {"Commander": 1, "Operative": 1, "Heavy": 2, "Special Forces": 3, "Support": 4, "Corps": 5}
            ai_units.sort(key=lambda x: rank_prio.get(x.get("rank"), 99))

            for i in range(min(len(ai_units), ai_orders_count)):
                ai_units[i]["order_token"] = True
        else:
            # Manueller Opponent - Befehle wählen lassen
            self.select_opponent_orders()

        self.create_order_pool()
        self.start_activation_phase()

    def take_manual_control(self):
        """Übernehme manuell die Kontrolle über AI-Einheit"""
        if self.active_side == "Opponent":
            # AI temporär deaktivieren für diese Aktivierung
            self.manual_override = True
            messagebox.showinfo("Manuelle Kontrolle", f"Du übernimmst manuell die Kontrolle über {self.active_unit['name']}")
            # UI aktualisieren
            self.update_actions_ui()

    def select_opponent_orders(self):
        pips = self.current_command_card["opponent"].get("pips", 4)
        orders_count = 3 if pips == 3 else (2 if pips == 2 else 1)
        
        # Dialog für Befehlswahl
        order_dialog = tk.Toplevel(self.root)
        order_dialog.title("Spieler 2 - Befehle erteilen")
        order_dialog.geometry("500x600")
        order_dialog.transient(self.root)
        order_dialog.grab_set()
        
        tk.Label(order_dialog, text=f"Spieler 2: Wähle {orders_count} Einheit(en) für Befehle", 
                font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        tk.Label(order_dialog, text=f"Kommandokarte: {self.current_command_card['opponent']['name']} ({pips}•)", 
                font=("Segoe UI", 12), fg="blue").pack(pady=5)
        
        # Checkbox-Liste für Opponent-Einheiten
        opponent_order_vars = []
        available_units = [u for u in self.opponent_army["units"] if u["current_hp"] > 0]
        
        for unit in available_units:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(order_dialog, 
                text=f"{unit['name']} ({unit.get('rank', 'Unknown')})",
                variable=var, font=("Segoe UI", 11))
            chk.pack(anchor="w", padx=20, pady=2)
            opponent_order_vars.append({"var": var, "unit": unit})
        
        def confirm_orders():
            selected = [item for item in opponent_order_vars if item["var"].get()]
            if len(selected) > orders_count:
                messagebox.showwarning("Zu viele Befehle", f"Du kannst nur {orders_count} Befehl(e) erteilen!")
                return
            elif len(selected) == 0:
                messagebox.showwarning("Keine Befehle", "Du musst mindestens einen Befehl erteilen!")
                return
            
            # Befehle anwenden
            for item in selected:
                item["unit"]["order_token"] = True
                
            order_dialog.destroy()
        
        tk.Button(order_dialog, text="Befehle bestätigen", command=confirm_orders,
                 bg="#4CAF50", fg="white", font=("Segoe UI", 12)).pack(pady=20)
        
        # Wait for dialog to close
        order_dialog.wait_window()

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
                tk.Label(f_acts, text="--- Wähle Einheit (Offener Befehl) ---").pack(pady=10)
                for u in current_army["units"]:
                    if u.get("order_token") and not u.get("activated") and u["current_hp"] > 0:
                        tk.Button(f_acts, text=f"Aktiviere: {u['name']}", command=lambda unit=u: self.activate_unit(unit, self.active_turn_player)).pack(fill="x", pady=2)

            # No big pass button - players alternate after each unit

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
            logging.info(f"AI activating unit: {unit_to_activate['name']}")
            self.activate_unit(unit_to_activate, "Opponent")
        else:
            # No units left? Check if player has units - if yes, pass turn, if no, end phase
            p_face_up = any(u.get("order_token") and not u.get("activated") and u["current_hp"] > 0 for u in self.player_army["units"])
            p_pool = any(t["side"] == "Player" for t in self.order_pool)
            p_rem = p_face_up or p_pool
            
            if p_rem:
                logging.info("AI passing turn (no units left, player has units).")
                self.pass_turn()
            else:
                logging.info("AI and Player both done, ending phase.")
                self.end_phase()

    def pass_turn(self):
        # This is for the big "Pass Turn" button - mark all remaining units as activated
        current_army = self.player_army if self.active_turn_player == "Player" else self.opponent_army
        
        for unit in current_army["units"]:
            if not unit.get("activated") and unit["current_hp"] > 0:
                unit["activated"] = True
        
        # Remove current player's tokens from order pool
        self.order_pool = [t for t in self.order_pool if t["side"] != self.active_turn_player]
        
        # Check if all units are activated
        p_remaining = any(not u.get("activated") and u["current_hp"] > 0 for u in self.player_army["units"])
        o_remaining = any(not u.get("activated") and u["current_hp"] > 0 for u in self.opponent_army["units"])
        
        if not p_remaining and not o_remaining:
            # All units activated - end round
            self.end_phase()
        else:
            # Check if other player still has units
            if (self.active_turn_player == "Player" and o_remaining) or (self.active_turn_player == "Opponent" and p_remaining):
                # Other player continues
                self.active_turn_player = "Opponent" if self.active_turn_player == "Player" else "Player"
                self.start_turn()
            else:
                # Both sides are done - end round
                self.end_phase()

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
        try:
            if courage == "-" or courage == "" or courage is None:
                c_val = 1
            else:
                c_val = int(courage)
            if unit["suppression"] >= 2 * c_val:
                self.is_panicked = True
        except (ValueError, TypeError):
            pass

        # Suppressed?
        self.is_suppressed = False
        try:
            if courage == "-" or courage == "" or courage is None:
                c_val = 1
            else:
                c_val = int(courage)
            if unit["suppression"] >= c_val:
                self.is_suppressed = True
                self.actions_remaining -= 1
        except (ValueError, TypeError):
            pass

    def update_actions_ui(self):
        # Check if frame_center still exists and active_unit is valid
        try:
            if not hasattr(self, 'frame_center') or not self.frame_center.winfo_exists() or not self.active_unit:
                return
        except tk.TclError:
            return
            
        # Clear specific frame or rebuild
        # Simplified: rebuild center bottom
        # ...

        f_status = tk.Frame(self.frame_center, bg="#eee", pady=5)
        f_status.pack(fill="x")

        # Show current unit's markers
        aim_count = self.active_unit.get("aim", 0)
        dodge_count = self.active_unit.get("dodge", 0)
        suppression_count = self.active_unit.get("suppression", 0)
        
        status_text = f"Aktionen: {self.actions_remaining}"
        if aim_count > 0:
            status_text += f" | 🎯 Zielen: {aim_count}"
        if dodge_count > 0:
            status_text += f" | 💨 Ausweichen: {dodge_count}"
        if suppression_count > 0:
            status_text += f" | 📉 Niederhalten: {suppression_count}"
            
        tk.Label(f_status, text=status_text, font=("bold"), bg="#eee").pack()
        
        if self.is_panicked:
            tk.Label(f_status, text="PANIK! Keine Aktionen.", fg="red", bg="#eee").pack()
        if self.is_suppressed:
            tk.Label(f_status, text="NIEDERGEHALTEN (-1 Aktion)", fg="orange", bg="#eee").pack()

        f_acts = tk.Frame(self.frame_center)
        f_acts.pack(pady=10)

        if (self.active_side == "Player" or (self.active_side == "Opponent" and not self.ai_enabled.get()) or getattr(self, 'manual_override', False)) and not self.is_panicked and self.actions_remaining > 0:
            btn_cfg = {"font": ("Segoe UI", 10), "width": 15, "bg": "#2196F3", "fg": "white"}

            if self.active_side == "Opponent":
                tk.Label(f_acts, text="Manueller Opponent-Modus:", font=("Segoe UI", 12, "bold"), fg="orange").grid(row=0, column=0, columnspan=2, pady=5)
                start_row = 1
            else:
                start_row = 0

            tk.Button(f_acts, text="Bewegung", command=lambda: self.perform_action("Move"), **btn_cfg).grid(row=start_row, column=0, padx=5, pady=5)
            tk.Button(f_acts, text="Angriff", command=lambda: self.perform_action("Attack"), **btn_cfg).grid(row=start_row, column=1, padx=5, pady=5)
            tk.Button(f_acts, text="Zielen (Aim)", command=lambda: self.perform_action("Aim"), **btn_cfg).grid(row=start_row+1, column=0, padx=5, pady=5)
            tk.Button(f_acts, text="Ausweichen (Dodge)", command=lambda: self.perform_action("Dodge"), **btn_cfg).grid(row=start_row+1, column=1, padx=5, pady=5)
            tk.Button(f_acts, text="Bereitschaft", command=lambda: self.perform_action("Standby"), **btn_cfg).grid(row=start_row+2, column=0, padx=5, pady=5)
            tk.Button(f_acts, text="Erholung", command=lambda: self.perform_action("Recover"), **btn_cfg).grid(row=start_row+2, column=1, padx=5, pady=5)
            tk.Button(f_acts, text="Interaktion", command=lambda: self.perform_action("Interact"), bg="#795548", fg="white", font=("Segoe UI", 10), width=15).grid(row=start_row+3, column=0, padx=5, pady=5)
            tk.Button(f_acts, text="Nahkampf", command=lambda: self.perform_action("Melee"), bg="#8D6E63", fg="white", font=("Segoe UI", 10), width=15).grid(row=start_row+3, column=1, padx=5, pady=5)

            # Pass Button für einzelne Einheit
            tk.Button(f_acts, text="Einheit Passen", command=self.pass_current_unit, bg="#FF9800", fg="white", font=("bold")).grid(row=start_row+4, column=0, padx=5, pady=5)
            tk.Button(f_acts, text="Aktivierung Beenden", command=self.end_activation, bg="#F44336", fg="white", font=("bold")).grid(row=start_row+4, column=1, padx=5, pady=5)

        elif (self.active_side == "Player" or (self.active_side == "Opponent" and not self.ai_enabled.get()) or getattr(self, 'manual_override', False)) and (self.is_panicked or self.actions_remaining <= 0):
             tk.Button(f_acts, text="Einheit Passen", command=self.pass_current_unit, bg="#FF9800", fg="white", font=("bold")).pack(pady=5)
             tk.Button(f_acts, text="Aktivierung Beenden", command=self.end_activation, bg="#F44336", fg="white", font=("bold")).pack()
        elif self.active_side == "Opponent" and self.ai_enabled.get():
            # AI ist aktiv - zeige Status
            tk.Label(f_acts, text="🤖 AI denkt nach...", font=("Segoe UI", 14, "bold"), fg="blue").pack(pady=20)
            tk.Button(f_acts, text="AI Überspringen (Manuell übernehmen)", 
                     command=self.take_manual_control, bg="#FF5722", fg="white").pack(pady=10)

    def perform_action(self, action_type):
        if self.actions_remaining <= 0 or not self.active_unit: 
            return

        # Reduce actions immediately (except Attack which might cancel?)
        # For simplicity, reduce now.

        msg = f"Action: {action_type} for {self.active_unit['name']}"
        logging.info(msg)

        if action_type == "Move":
            self.open_move_dialog()
            return # Don't decrement yet, wait for dialog
        elif action_type == "Attack":
            self.open_attack_dialog()
            return # Don't decrement yet
        elif action_type == "Aim":
            self.active_unit["aim"] = self.active_unit.get("aim", 0) + 1
            messagebox.showinfo("Zielen", f"{self.active_unit['name']} erhält 1 Zielmarker.\nGesamt: 🎯{self.active_unit['aim']}")
        elif action_type == "Dodge":
            self.active_unit["dodge"] = self.active_unit.get("dodge", 0) + 1
            messagebox.showinfo("Ausweichen", f"{self.active_unit['name']} erhält 1 Ausweichmarker.\nGesamt: 💨{self.active_unit['dodge']}")
        elif action_type == "Interact":
            # Neue Interaktions-Aktion
            self.open_interaction_dialog()
            return # Don't decrement yet, wait for dialog
        elif action_type == "Melee":
            # Nahkampf-Aktion
            self.open_melee_dialog()
            return # Don't decrement yet, wait for dialog
            return # Don't decrement yet, wait for dialog
        elif action_type == "Standby":
            # Bereitschafts-Mechanik: Einheit kann später reagieren
            self.active_unit["standby"] = True
            self.active_unit["dodge"] = self.active_unit.get("dodge", 0) + 1  # Gratis Dodge
            messagebox.showinfo("Bereitschaft", f"{self.active_unit['name']} geht in Bereitschaft!\n\n🛡️ Effekte:\n• Erhält 💨 Dodge-Marker\n• Kann außerhalb der Aktivierung reagieren\n• ⏸️ Bereitschaftsmarker bis zur nächsten Aktion")
        elif action_type == "Recover":
            # Rally-Mechanik: Erholung von Suppression
            old_suppression = self.active_unit.get("suppression", 0)
            if old_suppression > 0:
                # Entferne 2 Suppression (oder alle wenn weniger als 2)
                removed = min(old_suppression, 2)
                self.active_unit["suppression"] = old_suppression - removed
                
                # Panic-Zustand zurücksetzen wenn Suppression unter Courage fällt
                try:
                    courage_value = self.active_unit.get("courage", 1)
                    if courage_value == "-" or courage_value == "" or courage_value is None:
                        courage = 1
                    else:
                        courage = int(courage_value)
                    if self.active_unit["suppression"] < courage:
                        self.active_unit.pop("panic_state", None)
                except (ValueError, TypeError):
                    pass
                    
                messagebox.showinfo("Erholung", f"{self.active_unit['name']} erholt sich!\n\n🛡️ Rally-Effekte:\n• -{removed} 📉 Suppression\n• Gesamt: {self.active_unit['suppression']}\n• Panic-Zustand zurückgesetzt")
            else:
                # Keine Suppression: Erhält Aim-Marker
                self.active_unit["aim"] = self.active_unit.get("aim", 0) + 1
                messagebox.showinfo("Erholung", f"{self.active_unit['name']} fokussiert sich!\n\n🛡️ Rally ohne Suppression:\n• +1 🎯 Ziel-Marker\n• Gesamt: {self.active_unit['aim']}")

        # Standby-Marker entfernen nach jeder Aktion (außer Standby selbst)
        if action_type != "Standby" and self.active_unit and self.active_unit.get("standby", False):
            self.active_unit.pop("standby", None)
        
        # Decrement is handled by dialog callback for Move/Attack
        if action_type not in ["Move", "Attack"]:
            self.actions_remaining -= 1
            self.update_actions_ui()
            self.update_trees()

    def pass_current_unit(self):
        # Mark only the current unit as activated (pass without actions)
        if self.active_unit:
            self.active_unit["activated"] = True
            logging.info(f"Unit {self.active_unit['name']} passed (no actions taken)")
            # Update tree to show new status
            self.update_trees()
        
        # Continue with next player's turn
        self.check_and_continue_turn()
    
    def end_activation(self):
        # Reset manual override
        if hasattr(self, 'manual_override'):
            del self.manual_override
            
        # End effects
        if self.is_panicked:
            # Remove suppression = courage
            try:
                courage_value = self.active_unit.get("courage", 1)
                if courage_value == "-" or courage_value == "" or courage_value is None:
                    val = 1
                else:
                    val = int(courage_value)
                self.active_unit["suppression"] = max(0, self.active_unit["suppression"] - val)
            except: pass

        # Mark unit as activated
        if self.active_unit:
            self.active_unit["activated"] = True
            logging.info(f"Unit {self.active_unit['name']} finished activation")
            # Update tree to show new status
            self.update_trees()
        
        # Prüfe Bereitschafts-Reaktionen bevor der nächste Zug beginnt
        self.check_standby_reactions()
        
        # Continue with next player's turn
        self.check_and_continue_turn()
    
    def check_and_continue_turn(self):
        self.active_unit = None
        
        # Check if all units are activated
        p_remaining = any(not u.get("activated") and u["current_hp"] > 0 for u in self.player_army["units"])
        o_remaining = any(not u.get("activated") and u["current_hp"] > 0 for u in self.opponent_army["units"])
        
        if not p_remaining and not o_remaining:
            # All units activated - end round
            self.end_phase()
        else:
            # Switch to the other player
            self.active_turn_player = "Opponent" if self.active_turn_player == "Player" else "Player"
            
            # Check if current player has remaining units
            current_remaining = p_remaining if self.active_turn_player == "Player" else o_remaining
            
            if not current_remaining:
                # Current player has no units left, switch back to other player
                self.active_turn_player = "Opponent" if self.active_turn_player == "Player" else "Player"
            
            # Continue with next turn
            self.start_turn()
    
    def open_interaction_dialog(self):
        """Dialog für Interaktions-Aktionen (Bomben, Objekte, etc.)"""
        top = tk.Toplevel(self.root)
        top.title("Interaktion")
        top.geometry("400x500")
        
        tk.Label(top, text=f"{self.active_unit['name']} - Interaktion", font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        # Interaktionsoptionen
        options_frame = tk.Frame(top)
        options_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(options_frame, text="Wähle Interaktionstyp:", font=("Segoe UI", 12, "bold")).pack(pady=5)
        
        interaction_var = tk.StringVar(value="activate")
        
        # Verschiedene Interaktionstypen
        interactions = [
            ("activate", "🟢 Objekt aktivieren (Bomben, Terminals, etc.)"),
            ("deactivate", "🔴 Objekt deaktivieren (Sicherheitssysteme, etc.)"),
            ("claim", "🏴 Missionsziel beanspruchen"),
            ("repair", "🔧 Reparieren (Fahrzeuge, Ausrüstung)"),
            ("hack", "💻 Hacken (Computer, Droiden)"),
            ("search", "🔍 Durchsuchen (Container, Gebäude)"),
            ("use_equipment", "🎒 Ausrüstung benutzen")
        ]
        
        for value, text in interactions:
            tk.Radiobutton(options_frame, text=text, variable=interaction_var, value=value, 
                          font=("Segoe UI", 10), anchor="w").pack(fill="x", pady=2)
        
        # Zusätzliche Details
        details_frame = tk.Frame(top)
        details_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(details_frame, text="Beschreibung (optional):", font=("Segoe UI", 10)).pack(anchor="w")
        details_entry = tk.Entry(details_frame, width=50)
        details_entry.pack(fill="x", pady=5)
        
        # Buttons
        button_frame = tk.Frame(top)
        button_frame.pack(pady=20)
        
        def execute_interaction():
            interaction_type = interaction_var.get()
            details = details_entry.get().strip()
            
            # Führe Interaktion durch
            interaction_names = {
                "activate": "Aktivierung",
                "deactivate": "Deaktivierung", 
                "claim": "Beanspruchung",
                "repair": "Reparatur",
                "hack": "Hack",
                "search": "Durchsuchung",
                "use_equipment": "Ausrüstung"
            }
            
            name = interaction_names.get(interaction_type, "Interaktion")
            message = f"{self.active_unit['name']} führt {name} durch."
            if details:
                message += f"\n\n📝 Details: {details}"
            
            # Spezielle Effekte je nach Typ
            if interaction_type == "claim":
                message += "\n\n🏴 Missionsziel beansprucht! Überprüfe Siegbedingungen."
            elif interaction_type == "hack":
                message += "\n\n💻 Hack erfolgreich! Ziel unter deiner Kontrolle."
            elif interaction_type == "repair":
                message += "\n\n🔧 Reparatur abgeschlossen! Ziel wieder funktionsfähig."
            elif interaction_type == "use_equipment":
                self.open_equipment_dialog()
                top.destroy()
                return
            
            top.destroy()
            self.actions_remaining -= 1
            self.update_actions_ui()
            messagebox.showinfo("Interaktion", message)
        
        tk.Button(button_frame, text="INTERAKTION AUSFÜHREN", command=execute_interaction, 
                 bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        tk.Button(button_frame, text="Abbrechen", command=top.destroy, 
                 bg="#9E9E9E", fg="white").pack(side="left", padx=5)
    
    def open_equipment_dialog(self):
        """Dialog für Ausrüstungsnutzung"""
        top = tk.Toplevel(self.root)
        top.title("Ausrüstung benutzen")
        top.geometry("500x600")
        
        tk.Label(top, text=f"{self.active_unit['name']} - Ausrüstung", font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        # Verfügbare Ausrüstung anzeigen
        equipment_frame = tk.Frame(top)
        equipment_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(equipment_frame, text="Verfügbare Ausrüstung:", font=("Segoe UI", 12, "bold")).pack(pady=5)
        
        # Equipment aus Upgrades extrahieren
        equipment_list = []
        upgrades = self.active_unit.get("upgrades", [])
        
        # Standard-Ausrüstung basierend auf Einheitentyp
        unit_type = self.active_unit.get("rank", "Corps")
        if unit_type in ["Commander", "Operative"]:
            equipment_list.extend(["Kommando-Kit", "Taktische Ausrüstung"])
        
        for upgrade in upgrades:
            if isinstance(upgrade, str):
                # Vereinfachte Extraktion von Equipment-Namen
                clean_name = upgrade.split('(')[0].strip()
                if any(keyword in clean_name.lower() for keyword in 
                      ['granate', 'mine', 'kit', 'ausrüstung', 'equipment', 'device']):
                    equipment_list.append(clean_name)
        
        # Standard Equipment falls keine gefunden
        if not equipment_list:
            equipment_list = ["Standard-Kit", "Erste-Hilfe", "Kommunikationsgerät"]
        
        equipment_var = tk.StringVar()
        for i, equipment in enumerate(equipment_list[:8]):  # Max 8 Ausrüstungsgegenstände
            tk.Radiobutton(equipment_frame, text=f"⚙️ {equipment}", variable=equipment_var, 
                          value=equipment, font=("Segoe UI", 10), anchor="w").pack(fill="x", pady=2)
        
        # Effekte
        effects_frame = tk.Frame(top)
        effects_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(effects_frame, text="Mögliche Effekte:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        effects_text = tk.Text(effects_frame, height=6, width=50)
        effects_text.pack(fill="x", pady=5)
        effects_text.insert("1.0", "• Heilen von 1-2 HP\n• Zusätzliche Angriffswürfel\n• Bonus auf Verteidigung\n• Temporäre Fähigkeiten\n• Entfernung von Suppressions\n• Bewegungsbonus")
        effects_text.config(state="disabled")
        
        # Buttons
        button_frame = tk.Frame(top)
        button_frame.pack(pady=20)
        
        def use_equipment():
            import random
            selected = equipment_var.get()
            if not selected:
                messagebox.showwarning("Fehler", "Bitte wähle Ausrüstung aus.")
                return
            
            # Ausrüstungseffekte
            effects = []
            if "granate" in selected.lower() or "mine" in selected.lower():
                effects.append("💥 Explosionsschaden in Bereich")
            elif "erste" in selected.lower() or "hilfe" in selected.lower():
                heal_amount = random.randint(1, 2)
                old_hp = self.active_unit["current_hp"]
                max_hp = self.active_unit["hp"]
                self.active_unit["current_hp"] = min(max_hp, old_hp + heal_amount)
                effects.append(f"❤️ Heilung: +{heal_amount} HP")
            elif "kit" in selected.lower():
                # Entferne Suppression
                old_supp = self.active_unit.get("suppression", 0)
                if old_supp > 0:
                    self.active_unit["suppression"] = max(0, old_supp - 1)
                    effects.append(f"🧘 Suppression reduziert: -{1}")
                # Bonus Aim
                self.active_unit["aim"] = self.active_unit.get("aim", 0) + 1
                effects.append("🎯 +1 Zielmarker")
            else:
                effects.append("⚙️ Spezialeffekt angewandt")
            
            top.destroy()
            self.actions_remaining -= 1
            self.update_actions_ui()
            self.update_trees()
            
            messagebox.showinfo("Ausrüstung benutzt", 
                f"{self.active_unit['name']} benutzt {selected}\n\n" +
                "\n".join(effects))
        
        tk.Button(button_frame, text="AUSRÜSTUNG BENUTZEN", command=use_equipment, 
                 bg="#FF9800", fg="white", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        tk.Button(button_frame, text="Abbrechen", command=top.destroy, 
                 bg="#9E9E9E", fg="white").pack(side="left", padx=5)

    def ai_perform_actions(self):
        # Enhanced AI Decision Making with improved movement and targeting
        unit_name = self.active_unit["name"]
        instructions = []

        if self.is_panicked:
            instructions.append("1. PANIK: Einheit flieht (Sammeln von Mut).")
            instructions.append("2. Wirft alle Missionsziele ab.")
        else:
            # Enhanced AI Decision Making
            is_melee = False
            has_ranged = False
            max_range = 0
            
            # Alle Bodeneinheiten können Nahkampf (außer Fahrzeuge)
            unit_type = self.active_unit.get("type", "trooper")
            can_melee = unit_type.lower() not in ["vehicle", "speeder", "walker", "creature"]
            
            if "weapons" in self.active_unit:
                for w in self.active_unit["weapons"]:
                    weapon_range = w["range"][1]
                    if weapon_range > max_range: 
                        max_range = weapon_range
                    if w["range"][0] == 0: 
                        is_melee = True
                    if weapon_range > 1:
                        has_ranged = True
            
            # AI Strategy basierend auf Situation
            enemy_in_range = self.check_enemies_in_range()
            # Entferne problematische Methodenaufrufe für physisches Spiel
            # closest_enemy = self.find_closest_enemy()
            # mission_objectives = self.get_mission_objectives()
            
            if not enemy_in_range:
                # Keine Feinde in Reichweite - Intelligente Bewegung
                instructions.append("🔄 KEINE FEINDE IN REICHWEITE:")
                instructions.append("1. BEWEGUNG: Auf nächsten Feind zu oder Missionsziel")
                instructions.append("2. Nach Bewegung: Erneut Reichweite prüfen")
                if can_melee:
                    instructions.append("3. NAHKAMPF: Bei Kontakt (alle Bodeneinheiten)")
                instructions.append("4. ZIELEN oder AUSRÜSTUNG: Falls kein Angriff möglich")
                
                # Automatische Bewegung zur nächsten Einheit
                if closest_enemy:
                    self.auto_move_to_target(closest_enemy)
                    
            elif is_melee or can_melee:
                # Nahkampf bevorzugen - entferne self.enemy_in_melee_range() Aufruf
                # Nahkampf bevorzugen
                instructions.append("⚔️ NAHKAMPF STRATEGIE:")
                instructions.append("1. NAHKAMPF-ANGRIFF: Hoher Schaden, kann nicht geblockt werden")
                instructions.append("2. Alle Bodeneinheiten können Nahkampf ausführen")
                instructions.append("3. ZIELEN: Falls Angriff nicht optimal")
                
                # Automatischer Nahkampf-Versuch
                if self.enemy_in_melee_range():
                    self.auto_attempt_melee()
                    
            elif has_ranged:
                # Fernkampf mit intelligenter Zielwahl
                instructions.append("🎯 FERNKAMPF STRATEGIE:")
                instructions.append("1. ZIELEN: Für bessere Trefferchance")
                instructions.append(f"2. ANGRIFF: Fernwaffen (Reichweite {max_range})")
                instructions.append("3. AUSRÜSTUNG: Nutze verfügbare Items")
                
                # Automatisches Zielen und Angreifen
                self.auto_aim_and_attack()
                
            else:
                # Support und Ausrüstung
                instructions.append("🔧 SUPPORT STRATEGIE:")
                instructions.append("1. AUSRÜSTUNG: Nutze Unterstützungs-Items")
                instructions.append("2. BEWEGUNG: Position für Support")
                instructions.append("3. AUSWEICHEN oder BEREITSCHAFT")

        # Show instructions für physisches Spiel
        instruction_text = f"🤖 KI-Aktivierung: {unit_name}\\n\\n" + "\\n".join(instructions)
        instruction_text += "\\n\\n📋 Führe diese Aktionen auf dem physischen Spieltisch aus."
        instruction_text += "\\n🎲 Verwende die Aktions-Buttons um Ergebnisse einzutragen."
        
        messagebox.showinfo("AI Zug", instruction_text)

        # Legacy AI logic for compatibility  
        if not self.is_panicked and is_melee and max_range < 2:
            # Melee Attack Query
            self.ai_query_targets(self.active_unit, is_melee=True)
        elif not self.is_panicked and max_range >= 2:
            # Ranged Attack Query
            self.ai_query_targets(self.active_unit, is_melee=False)
        else:
            # No attack possible - show options
            msg = f"Einheit: {unit_name}\\n\\n" + "\\n".join(instructions) + "\\n\\nBitte führe diese Aktionen auf dem Tisch aus."
            messagebox.showinfo("AI Zug Anweisung", msg)

    def find_closest_enemy(self):
        """Findet den nächsten Feind für AI-Bewegung (vereinfacht)"""
        return {"name": "Feindliche Einheit", "distance": random.randint(2, 6)}

    def get_mission_objectives(self):
        """Gibt verfügbare Missionsziele zurück (vereinfacht)"""
        if self.mission_data:
            return [{"name": "Missionsziel", "distance": random.randint(2, 5)}]
        return []

    def enemy_in_melee_range(self):
        """Prüft ob Feinde in Nahkampf-Reichweite sind (vereinfacht)"""
        return random.random() < 0.3

    def find_best_ranged_target(self):
        """Findet das beste Fernkampf-Ziel (vereinfacht)"""
        return {"name": "Bestes Ziel", "priority": 75}

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
            messagebox.showinfo("AI Info", "Keine Ziele in Reichweite. AI sollte Bewegung oder andere Aktion durchführen.\n\nBitte führe eine passende Aktion für die AI-Einheit durch und klicke dann die entsprechenden Aktions-Buttons.")
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
        top.geometry("450x400")

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

        # Reset Active View (safe check if they exist)
        if hasattr(self, 'lbl_active_name'):
            self.lbl_active_name.config(text="-")
        if hasattr(self, 'lbl_active_stats'):
            self.lbl_active_stats.config(text="")
        self.active_unit = None

        # Next Round Button - use configurable max rounds
        max_rounds = self.mission_data.get('rounds', 6) if self.mission_data else 6
        if self.round_number >= max_rounds:
            tk.Label(self.frame_center, text=f"SPIELENDE (Runde {max_rounds} erreicht)", font=("Segoe UI", 24, "bold"), fg="red").pack(pady=20)
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

        # UI Updates (safe check if labels exist)
        color = "#2196F3" if side == "Player" else "#F44336"
        if hasattr(self, 'lbl_active_name'):
            self.lbl_active_name.config(text=f"{unit['name']} ({side})", fg=color)

        stats_text = (f"Bewegung: {unit.get('speed', '-')}\n"
                      f"Verteidigung: {unit.get('defense', '-')}\n"
                      f"HP: {unit['current_hp']}/{unit['hp']} | Mut: {unit['courage']}\n"
                      f"Keywords: {unit.get('info', '')}")
        if hasattr(self, 'lbl_active_stats'):
            self.lbl_active_stats.config(text=stats_text)

        # Update Trees (um 'Aktiviert' Status zu zeigen)
        self.update_trees()

        if hasattr(self, 'lbl_phase'):
            self.lbl_phase.config(text=f"Pool: {len(self.order_pool)} verbleibend")

        # Buttons aktivieren
        if hasattr(self, 'btn_attack'):
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

    def update_score_display(self):
        """Aktualisiere die Punkteanzeige"""
        self.lbl_score.config(text=f"Spieler: {self.player_score} | Gegner: {self.opponent_score}")

    def open_attack_dialog(self, pre_target=None, pre_weapon=None):
        if not self.active_unit: return

        # Callback for completion
        def on_complete():
            self.actions_remaining -= 1
            self.update_actions_ui()
            self.update_trees()

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
                # Load Dodge markers from target unit
                dodge_count = target_unit.get("dodge", 0)
                var_dodge.set(dodge_count)

        cb_target.bind("<<ComboboxSelected>>", on_target_select)

        # Deckung / Token UI
        tk.Label(frame_target, text="Deckung (Cover):").grid(row=2, column=0, sticky="w")
        tk.Radiobutton(frame_target, text="Keine", variable=var_cover, value=0).grid(row=2, column=1, sticky="w")
        tk.Radiobutton(frame_target, text="Leicht (1)", variable=var_cover, value=1).grid(row=2, column=2, sticky="w")
        tk.Radiobutton(frame_target, text="Schwer (2)", variable=var_cover, value=2).grid(row=2, column=3, sticky="w")

        tk.Label(frame_target, text="Ausweichen-Marker (Dodge):").grid(row=3, column=0, sticky="w")
        # Auto-fill dodge markers if pre_target is set
        initial_dodge = 0
        if pre_target:
            target_unit = next((u for u in targets if u["name"] == pre_target), None)
            if target_unit:
                initial_dodge = target_unit.get("dodge", 0)
        var_dodge = tk.IntVar(value=initial_dodge)
        tk.Spinbox(frame_target, from_=0, to=10, textvariable=var_dodge, width=5).grid(row=3, column=1, sticky="w")

        tk.Label(frame_target, text="Zielen-Marker (Aim) [Angreifer]:").grid(row=4, column=0, sticky="w", pady=(10,0))
        var_aim = tk.IntVar(value=0)
        tk.Spinbox(frame_target, from_=0, to=10, textvariable=var_aim, width=5).grid(row=4, column=1, sticky="w", pady=(10,0))

        # Buttons Control Variable
        self.attack_rolled = False
        
        # Auto-fill Aim markers if unit has them
        unit_aim = unit.get("aim", 0)
        if unit_aim > 0:
            var_aim.set(unit_aim)
        
        # Display current marker status in UI
        if unit_aim > 0 or unit.get("dodge", 0) > 0 or unit.get("suppression", 0) > 0:
            marker_status = []
            if unit_aim > 0: marker_status.append(f"🎯{unit_aim}")
            if unit.get("dodge", 0) > 0: marker_status.append(f"💨{unit['dodge']}")
            if unit.get("suppression", 0) > 0: marker_status.append(f"📉{unit['suppression']}")
            tk.Label(frame_target, text=f"Angreifer-Marker: {' '.join(marker_status)}", 
                    fg="#4CAF50", font=("Segoe UI", 9, "bold")).grid(row=4, column=2, columnspan=2, sticky="w", pady=(10,0))

        # 3. ERGEBNIS BEREICH
        frame_result = tk.LabelFrame(top, text="3. Ergebnis", padx=10, pady=10, bg="#e0f7fa")
        frame_result.pack(fill="x", padx=10, pady=10)

        lbl_log = tk.Label(frame_result, text="Drücke 'WÜRFELN'...", bg="#e0f7fa", justify=tk.LEFT, font=("Consolas", 10))
        lbl_log.pack(anchor="w")

        # LOGIK
        def roll_attack():
            # 1. Pool bilden - KORREKTUR: Für jede Miniatur im Trupp
            pool = {"red": 0, "black": 0, "white": 0}
            selected_weapons = [w for w in weapon_vars if w["var"].get()]

            if not selected_weapons:
                messagebox.showwarning("Fehler", "Keine Waffe gewählt!")
                return

            # Miniaturenanzahl des angreifenden Trupps
            current_minis = unit.get("current_minis", unit.get("minis", 1))
            log_text = f"Angreifender Trupp: {unit['name']} ({current_minis} Miniaturen)\n"
            
            # Prüfe Panic-Zustand der angreifenden Einheit
            panic_state = unit.get("panic_state", "")
            if panic_state == "retreat":
                messagebox.showwarning("Panic", f"{unit['name']} ist im Rückzug und kann nicht angreifen!")
                return
            elif panic_state == "suppressed":
                log_text += "⚠️ Einheit ist unterdrückt - reduzierte Effektivität\n"

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

            # Weapon Keywords und Pool pro Miniatur
            for w in selected_weapons:
                wd = w["data"]
                # Würfel für jede Miniatur im Trupp hinzufügen
                for color, count in wd["dice"].items():
                    pool[color] += count * current_minis  # KORREKTUR: Multipliziere mit Miniaturenanzahl
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

            log_text += f"Basis-Würfelpool: {pool}\n"
            
            # SUPPRESSION-EFFEKTE auf Angreifer anwenden
            pool, suppression_log = self.apply_suppression_to_pool(pool, unit)
            if suppression_log:
                log_text += suppression_log

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

            log_text += f"Wurfergebnis: {results}\n"

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

            # SUPPRESSION - Erweiterte Mechanik
            suppr_val = 0
            # Standard: Wenn mindestens 1 Hit/Crit Ergebnis nach Verteidigung
            if total_hits > 0:
                suppr_val += 1

            # Keyword: Suppressive - Gibt +1 Suppression auch bei 0 Schaden
            suppressive_val = kw_map.get("Suppressive", 0) + kw_map.get("Niederhaltend", 0)
            if suppressive_val > 0:
                suppr_val += suppressive_val
                
            # Minimum 1 Suppression wenn Suppressive Waffe verwendet wurde
            if suppressive_val > 0 and suppr_val == 0:
                suppr_val = 1

            if suppr_val > 0:
                log_text += f"\n📉 Niederhalten: +{suppr_val}"
                if suppressive_val > 0:
                    log_text += f" (inkl. Niederhaltend {suppressive_val})"

            lbl_log.config(text=log_text, fg="red" if wounds > 0 else ("orange" if suppr_val > 0 else "green"))

            # Apply Button
            if target_unit and (wounds > 0 or suppr_val > 0):
                def apply_result():
                    eliminated_points = 0
                    
                    if wounds > 0:
                        remaining_damage = wounds
                        current_hp = target_unit["current_hp"]
                        max_hp = target_unit["hp"]
                        current_minis = target_unit.get("minis", 1)
                        
                        # Berechne Figuren-Verluste durch Überschaden
                        figures_lost = 0
                        
                        while remaining_damage > 0 and current_minis > 0:
                            if remaining_damage >= current_hp:
                                # Aktuelle Figur stirbt
                                remaining_damage -= current_hp
                                figures_lost += 1
                                current_minis -= 1
                                current_hp = max_hp  # Nächste Figur hat volle HP
                            else:
                                # Aktuelle Figur überlebt mit reduzierter HP
                                current_hp -= remaining_damage
                                remaining_damage = 0
                        
                        # Update Einheit
                        target_unit["minis"] = current_minis
                        target_unit["current_hp"] = current_hp
                        
                        # Punkte berechnen wenn Figuren sterben
                        if figures_lost > 0:
                            # Versuche verschiedene Möglichkeiten für Einheitskosten
                            unit_cost = target_unit.get("cost", 0)
                            if unit_cost == 0:
                                unit_cost = target_unit.get("points", 0)
                            if unit_cost == 0:
                                unit_cost = target_unit.get("pts", 0)
                            if unit_cost == 0:
                                # Fallback: Schätzung basierend auf Rang
                                rank = target_unit.get("rank", "Corps")
                                cost_estimates = {
                                    "Commander": 200, "Operative": 150, 
                                    "Corps": 60, "Special Forces": 80, 
                                    "Support": 40, "Heavy": 200
                                }
                                unit_cost = cost_estimates.get(rank, 60)
                            
                            original_minis = target_unit.get("original_minis", target_unit.get("minis", 1) + figures_lost)
                            target_unit["original_minis"] = original_minis  # Speichere Original für Punkteberechnung
                            points_per_figure = unit_cost / original_minis if original_minis > 0 else 0
                            eliminated_points = int(figures_lost * points_per_figure)
                            
                            # Punkte dem Angreifer gutschreiben
                            if unit in self.player_army["units"]:
                                # Spieler greift an, Opponent erhält Punkte
                                self.opponent_score = getattr(self, 'opponent_score', 0) + eliminated_points
                            else:
                                # Opponent greift an, Spieler erhält Punkte
                                self.player_score = getattr(self, 'player_score', 0) + eliminated_points
                            
                            # Aktualisiere Punkteanzeige
                            self.update_score_display()
                        
                        # Meldungen
                        if current_minis <= 0:
                            # Einheit vollständig eliminiert - aus Liste entfernen
                            if target_unit in self.player_army["units"]:
                                self.player_army["units"].remove(target_unit)
                            elif target_unit in self.opponent_army["units"]:
                                self.opponent_army["units"].remove(target_unit)
                            messagebox.showwarning("Truppe vernichtet!", 
                                f"{target_unit['name']} wurde vollständig eliminiert!\n{eliminated_points} Punkte gutgeschrieben!")
                        elif figures_lost > 0:
                            messagebox.showinfo("Verluste!", 
                                f"{target_unit['name']}: {figures_lost} Figur(en) eliminiert!\nVerbleibende: {current_minis}\n{eliminated_points} Punkte gutgeschrieben!")
                        
                    if suppr_val > 0:
                        target_unit["suppression"] = target_unit.get("suppression", 0) + suppr_val

                    # Remove used Aim markers
                    aim_used = var_aim.get()
                    if aim_used > 0:
                        unit["aim"] = max(0, unit.get("aim", 0) - aim_used)

                    # Remove used Dodge markers (they were already calculated in the attack)
                    dodges_available = var_dodge.get()
                    if dodges_available > 0:
                        # Dodge markers are consumed when used, clear them
                        target_unit["dodge"] = 0

                    # PANIC TEST - Wenn Suppression >= Courage
                    current_suppression = target_unit.get("suppression", 0)
                    try:
                        courage_value = target_unit.get("courage", 1)
                        if courage_value == "-" or courage_value == "" or courage_value is None:
                            courage = 1
                        else:
                            courage = int(courage_value)
                    except (ValueError, TypeError):
                        courage = 1  # Default fallback
                    
                    panic_message = ""
                    if current_suppression >= courage:
                        panic_message = self.perform_panic_test(target_unit)

                    self.update_trees()
                    message = f"{target_unit['name']}:\n-{wounds} HP\n+{suppr_val} Suppression (Total: {current_suppression})\nZielmarker verbraucht: {aim_used}"
                    if dodges_available > 0:
                        message += f"\nAusweichen-Marker verbraucht: {dodges_available}"
                    if panic_message:
                        message += f"\n\n🚨 PANIC TEST:\n{panic_message}"
                    
                    # Schließe Fenster SOFORT nach dem Anwenden
                    top.destroy()
                    on_complete() # Decrement Action
                    
                    # Zeige Ergebnis in einem neuen, kurzem Fenster
                    messagebox.showinfo("Angriff erfolgreich!", message)

                btn_apply = tk.Button(frame_result, text="ERGEBNIS ANWENDEN", bg="red", fg="white", command=apply_result)
                btn_apply.pack(pady=5)
            else:
                def close_no_effect():
                    # Consumes action even if missed
                    top.destroy()
                    on_complete()
                
                tk.Button(frame_result, text="Angriff beenden (Keine Wirkung)", 
                          bg="gray", fg="white", command=close_no_effect).pack(pady=5)

        btn_roll = tk.Button(frame_result, text="⚂ WÜRFELN", bg="#4CAF50", fg="white", command=roll_attack, font=("Segoe UI", 12, "bold"))
        btn_roll.pack(pady=5)

    def perform_panic_test(self, unit):
        """Führe einen Panic-Test durch wenn Suppression >= Courage"""
        import random
        
        suppression = unit.get("suppression", 0)
        
        # Robuste Courage-Konvertierung
        try:
            courage_value = unit.get("courage", 1)
            if courage_value == "-" or courage_value == "" or courage_value is None:
                courage = 1  # Standard-Fallback
            else:
                courage = int(courage_value)
        except (ValueError, TypeError):
            courage = 1  # Fallback bei ungültigen Werten
            
        panic_dice = suppression - courage
        
        # Würfle Panic-Würfel (weiße Würfel)
        results = []
        for _ in range(panic_dice):
            roll = random.randint(1, 6)
            if roll == 1:
                results.append("blank")
            else:
                results.append("success")
        
        panic_count = results.count("blank")
        message = f"Mut: {courage}, Niederhalten: {suppression}\n"
        message += f"Panic-Würfel: {panic_dice} ({results.count('blank')} blanks)\n\n"
        
        if panic_count == 0:
            message += "✅ KEIN PANIC - Einheit hält Stand!"
            return message
        
        # Panic-Effekte je nach Anzahl der blanks
        if panic_count >= 2:
            # Schwere Panik: Rückzug
            message += "🔥 SCHWERE PANIK (2+ blanks):\n"
            message += "• Einheit muss sich zurückziehen\n"
            message += "• Verliert alle Marker außer Suppression\n"
            message += "• Kann diese Runde nicht mehr aktivieren"
            
            # Entferne alle Marker außer Suppression
            unit["aim"] = 0
            unit["dodge"] = 0
            unit["standby"] = 0
            unit["panic_state"] = "retreat"  # Zustand für AI/UI
            
        else:
            # Leichte Panik: Suppression bleibt
            message += "⚠️ LEICHTE PANIK (1 blank):\n"
            message += "• Einheit ist unterdrückt\n"
            message += "• Verliert 1 Aktion diese Runde\n"
            message += "• Kann nicht zielen"
            
            # Entferne alle Aim-Marker
            unit["aim"] = 0
            unit["panic_state"] = "suppressed"  # Zustand für AI/UI
        
        return message
    
    def check_suppression_effects(self, unit):
        """Prüfe Suppression-Effekte auf Würfelpool"""
        suppression = unit.get("suppression", 0)
        if suppression == 0:
            return 0
            
        # Für jedes Suppression-Token: -1 Angriffswürfel
        return min(suppression, 2)  # Maximum 2 Würfel Reduktion
    
    def apply_suppression_to_pool(self, pool, unit):
        """Reduziere Würfelpool basierend auf Suppression"""
        reduction = self.check_suppression_effects(unit)
        if reduction == 0:
            return pool, ""
            
        # Reduziere Würfel (Priorität: weiß -> schwarz -> rot)
        original_total = sum(pool.values())
        log = f"🚫 Suppression-Effekt: -{reduction} Würfel\n"
        
        for color in ["white", "black", "red"]:
            while reduction > 0 and pool[color] > 0:
                pool[color] -= 1
                reduction -= 1
                
        new_total = sum(pool.values())
        if new_total < original_total:
            log += f"Würfelpool reduziert: {original_total} → {new_total}\n"
            
        return pool, log

    def check_standby_reactions(self):
        """Prüfe ob Bereitschafts-Reaktionen möglich sind"""
        # Finde alle Einheiten mit Bereitschafts-Marker
        standby_units = []
        
        for side in ["Player", "Opponent"]:
            if side == "Player":
                army = self.player_army["units"]
            else:
                army = self.opponent_army["units"]
                
            for unit in army:
                if unit.get("standby", False) and unit.get("current_hp", 0) > 0:
                    standby_units.append((side, unit))
        
        if standby_units:
            # Biete Bereitschafts-Reaktionen an
            reaction_text = "Bereitschafts-Reaktionen verfügbar:\n\n"
            for side, unit in standby_units:
                reaction_text += f"🛡️ {side}: {unit['name']}\n"
            reaction_text += "\nMöchtest du eine Bereitschafts-Reaktion durchführen?"
            
            if messagebox.askyesno("Bereitschaft", reaction_text):
                self.handle_standby_reaction(standby_units)
    
    def handle_standby_reaction(self, standby_units):
        """Handle Bereitschafts-Reaktion"""
        if len(standby_units) == 1:
            side, unit = standby_units[0]
        else:
            # Mehrere Einheiten - Spieler wählt
            choices = [f"{side}: {unit['name']}" for side, unit in standby_units]
            choice = tk.simpledialog.askstring("Bereitschafts-Reaktion", 
                f"Wähle reagierende Einheit:\n{chr(10).join(f'{i+1}. {c}' for i, c in enumerate(choices))}\n\nEingabe (1-{len(choices)}):")
            
            try:
                idx = int(choice) - 1
                side, unit = standby_units[idx]
            except (ValueError, IndexError, TypeError):
                return
        
        # Bereitschafts-Marker entfernen
        unit.pop("standby", None)
        
        # Temporäre Aktivierung für Bereitschafts-Reaktion
        old_active_side = self.active_side
        old_active_unit = self.active_unit
        
        self.active_side = side
        self.active_unit = unit
        self.actions_remaining = 1  # Nur eine Aktion
        
        messagebox.showinfo("Bereitschafts-Reaktion", 
            f"⏸️ {unit['name']} reagiert aus der Bereitschaft!\n\n🎯 Eine Aktion verfügbar")
        
        # UI aktualisieren für Reaktion
        self.update_trees()
    
    def check_enemies_in_range(self):
        """Prüfe ob Feinde in Waffenreichweite sind (Vereinfacht)"""
        # Vereinfachte Logik - in echter Implementation würde man
        # Spielbrett-Positionen und Distanzen berechnen
        if not self.active_unit or "weapons" not in self.active_unit:
            return False
        
        # Simuliere Reichweiten-Check
        # In echter Implementation: Berechne Distanzen auf dem Spielfeld
        max_range = 0
        for w in self.active_unit["weapons"]:
            if w["range"][1] > max_range:
                max_range = w["range"][1]
        
        # Heuristik: 70% Chance dass Feinde in Reichweite sind
        import random
        return random.random() < 0.7
    
    def enemy_in_melee_range(self):
        """Prüfe ob Feinde in Nahkampf-Reichweite (Kontakt) sind"""
        # Vereinfachte Logik - in echter Implementation würde man
        # Kontakt zwischen Einheiten auf dem Spielfeld prüfen
        
        # Heuristik: 30% Chance für Nahkampf-Kontakt
        import random
        return random.random() < 0.3
    
    def get_melee_weapons(self, unit):
        """Hole alle Nahkampf-Waffen einer Einheit"""
        melee_weapons = []
        
        # Prüfe explizite Nahkampf-Waffen
        if "weapons" in unit:
            for w in unit["weapons"]:
                if w["range"][0] == 0 and w["range"][1] <= 1:
                    melee_weapons.append(w)
        
        # Alle Bodeneinheiten haben Standard-Nahkampf
        unit_type = unit.get("type", "trooper")
        if unit_type.lower() not in ["vehicle", "speeder", "walker"] and not melee_weapons:
            # Standard Nahkampf für alle Infanterie
            standard_melee = {
                "name": "Unarmed Melee",
                "range": [0, 1],
                "dice": {"red": 1},
                "keywords": ["Melee"]
            }
            melee_weapons.append(standard_melee)
        
        return melee_weapons
    
    def update_score_display(self):
        """Update the score display in the UI"""
        if hasattr(self, 'lbl_score'):
            self.lbl_score.config(text=f"Spieler: {self.player_score} | Gegner: {self.opponent_score}")

    def open_interaction_dialog(self):
        """Öffnet Dialog für Interaktions-Aktionen"""
        interact_window = tk.Toplevel(self.root)
        interact_window.title("Interaktion - 1 Aktion")
        interact_window.geometry("400x500")
        interact_window.resizable(False, False)
        
        tk.Label(interact_window, text="Interaktions-Möglichkeiten", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        interactions = [
            ("Bomben/Sprengladung aktivieren", "explosive"),
            ("Bomben/Sprengladung deaktivieren", "defuse"), 
            ("Objekt aufheben", "pickup"),
            ("Objekt fallen lassen", "drop"),
            ("Schalter/Terminal bedienen", "terminal"),
            ("Tür öffnen/schließen", "door"),
            ("Fahrzeug besteigen", "embark"),
            ("Fahrzeug verlassen", "disembark"),
            ("Reparieren", "repair"),
            ("Missionsziel aktivieren", "objective")
        ]
        
        for interaction_name, interaction_type in interactions:
            btn = tk.Button(interact_window, text=interaction_name,
                          command=lambda t=interaction_type, n=interaction_name: self.execute_interaction(t, n, interact_window),
                          font=("Arial", 10), width=30, pady=5)
            btn.pack(pady=2)
        
        tk.Button(interact_window, text="Abbrechen", 
                 command=interact_window.destroy,
                 bg="#f44336", fg="white", font=("Arial", 12)).pack(pady=20)

    def execute_interaction(self, interaction_type, interaction_name, window):
        """Führt eine Interaktion aus"""
        unit_name = self.active_unit.get("name", "Unbekannt")
        
        # Erfolgs-Wahrscheinlichkeit basierend auf Einheit
        success_chance = 0.8  # Standard 80% Erfolgschance
        
        # Modifikationen basierend auf Einheit-Typ
        if "Engineer" in unit_name or "Technician" in unit_name:
            success_chance = 0.95  # Spezialisten haben höhere Erfolgsrate
        elif "Trooper" in unit_name:
            success_chance = 0.7   # Normale Truppen haben niedrigere Rate
        
        success = random.random() < success_chance
        
        if success:
            result = "erfolgreich"
            # Spezielle Effekte für verschiedene Interaktionen
            if interaction_type == "explosive":
                # Schade im Umkreis
                messagebox.showinfo("Explosion!", 
                              "BOOM! 💥\n\nExplosion verursacht Bereich-Schaden!\n(Details würden basierend auf Missionsziel implementiert)")
            elif interaction_type == "repair":
                # Repariere Fahrzeug oder Objekt
                messagebox.showinfo("Reparatur", 
                              "🔧 Reparatur erfolgreich!\n\nObjekt/Fahrzeug wurde repariert.")
        else:
            result = "fehlgeschlagen"
        
        messagebox.showinfo("Interaktion", 
                          f"{unit_name} hat versucht: {interaction_name}\n\nErgebnis: {result.title()}!")
        
        # Aktion verbrauchen und Fenster schließen
        self.actions_remaining = max(0, self.actions_remaining - 1)
        # self.update_center()  # Entfernt da Methode nicht existiert
        window.destroy()

    def open_melee_dialog(self):
        """Öffnet Nahkampf-Dialog für alle Bodeneinheiten"""
        if not self.active_unit:
            return
            
        melee_window = tk.Toplevel(self.root)
        melee_window.title("Nahkampf-Angriff")
        melee_window.geometry("450x400") 
        melee_window.resizable(False, False)
        
        tk.Label(melee_window, text="Nahkampf-Angriff", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Info über Nahkampf-Regeln
        info_text = """Nahkampf-Regeln:
• Nur gegen Einheiten in Reichweite 1
• Alle Bodeneinheiten können Nahkampf
• Würfel = Anzahl Miniaturen
• +1 Würfel wenn mehr Minis als Ziel
• Verteidiger kann zurückschlagen"""
        
        tk.Label(melee_window, text=info_text, 
                font=("Arial", 10), justify="left").pack(pady=10)
        
        # Ziel auswählen
        tk.Label(melee_window, text="Ziel auswählen:", 
                font=("Arial", 12, "bold")).pack(pady=(10,5))
        
        # Finde Ziele in Reichweite 1
        targets = self.get_melee_targets()
        
        if not targets:
            tk.Label(melee_window, text="Keine Ziele in Nahkampf-Reichweite!", 
                    fg="red", font=("Arial", 12)).pack(pady=10)
            tk.Button(melee_window, text="Schließen", 
                     command=melee_window.destroy).pack(pady=10)
            return
        
        target_var = tk.StringVar(value=targets[0] if targets else "")
        target_cb = ttk.Combobox(melee_window, textvariable=target_var, 
                               values=targets, state="readonly", width=30)
        target_cb.pack(pady=5)
        
        # Angriff ausführen
        def execute_melee():
            target = target_var.get()
            if target:
                self.execute_melee_attack(target)
                melee_window.destroy()
        
        tk.Button(melee_window, text="Nahkampf ausführen!", 
                 command=execute_melee,
                 bg="#F44336", fg="white", font=("Arial", 12, "bold")).pack(pady=20)
        
        tk.Button(melee_window, text="Abbrechen", 
                 command=melee_window.destroy,
                 bg="#757575", fg="white").pack(pady=5)

    def get_melee_targets(self):
        """Findet alle Einheiten in Nahkampf-Reichweite (simuliert)"""
        targets = []
        
        # Simuliere Ziele basierend auf Gegner-Armee
        enemy_army = self.opponent_army if self.active_side == "Player" else self.player_army
        
        for unit in enemy_army.get("units", []):
            if unit.get("current_hp", 0) > 0:  # Nur lebende Einheiten
                # Simuliere dass einige Einheiten in Reichweite sind
                if random.random() < 0.4:  # 40% Chance in Nahkampf-Reichweite
                    targets.append(unit.get("name", "Unbekannt"))
        
        return targets

    def execute_melee_attack(self, target_name):
        """Führt Nahkampf-Angriff aus"""
        if not self.active_unit:
            return
            
        attacker = self.active_unit
        attacker_name = attacker.get("name", "Unbekannt")
        attacker_minis = attacker.get("minis", 1)
        
        # Finde Ziel-Einheit
        enemy_army = self.opponent_army if self.active_side == "Player" else self.player_army
        target_unit = None
        
        for unit in enemy_army.get("units", []):
            if unit.get("name") == target_name:
                target_unit = unit
                break
        
        if not target_unit:
            messagebox.showerror("Fehler", "Ziel nicht gefunden!")
            return
            
        target_minis = target_unit.get("minis", 1)
        
        # Berechne Angriffs-Würfel (Basis = Anzahl Miniaturen)
        attack_dice = attacker_minis
        
        # Bonus wenn mehr Minis als Gegner
        if attacker_minis > target_minis:
            attack_dice += 1
            
        # Würfle für Angriff
        hits = 0
        for _ in range(attack_dice):
            if random.randint(1, 8) >= 4:  # 4+ zum Treffen
                hits += 1
        
        # Verteidigung
        defense_dice = target_minis
        blocks = 0
        for _ in range(defense_dice):
            if random.randint(1, 8) >= 5:  # 5+ zum Blocken  
                blocks += 1
        
        # Schaden berechnen
        damage = max(0, hits - blocks)
        
        # Schaden anwenden
        if damage > 0:
            self.apply_figure_damage(target_unit, damage)
        
        # Zurückschlag (falls Ziel noch lebt)
        counter_damage = 0
        if target_unit.get("current_hp", 0) > 0:
            counter_dice = target_unit.get("minis", 1)
            counter_hits = sum(1 for _ in range(counter_dice) if random.randint(1, 8) >= 5)
            counter_blocks = sum(1 for _ in range(attacker_minis) if random.randint(1, 8) >= 5)
            counter_damage = max(0, counter_hits - counter_blocks)
            
            if counter_damage > 0:
                self.apply_figure_damage(attacker, counter_damage)
        
        # Ergebnis anzeigen
        result_text = f"Nahkampf: {attacker_name} vs {target_name}\n\n"
        result_text += f"Angriff: {attack_dice} Würfel → {hits} Treffer\n"
        result_text += f"Verteidigung: {defense_dice} Würfel → {blocks} Blocks\n"
        result_text += f"Schaden an {target_name}: {damage}\n"
        
        if counter_damage > 0:
            result_text += f"\nZurückschlag: {counter_damage} Schaden an {attacker_name}"
        
        messagebox.showinfo("Nahkampf-Ergebnis", result_text)
        
        # Aktion verbrauchen
        self.actions_remaining = max(0, self.actions_remaining - 1)
        
        # Trees aktualisieren
        self.update_tree(self.tree_player, self.player_army["units"])
        self.update_tree(self.tree_opponent, self.opponent_army["units"])
        # self.update_center()  # Entfernt da Methode nicht existiert

if __name__ == "__main__":

        btn_roll = tk.Button(top, text="WÜRFELN", command=roll_attack, font=("Segoe UI", 12, "bold"), bg="#2196F3", fg="white")
        btn_roll.pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    
    # Check for mission file argument
    mission_file = None
    if len(sys.argv) > 1:
        mission_file = sys.argv[1]
        
    app = GameCompanion(root, mission_file=mission_file)
    root.mainloop()
