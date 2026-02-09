import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import logging

# PIL für Bildanzeige
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# =============================================================================
# TEIL 1: DIE DATENBANK (IMPORT)
# =============================================================================

# Import LegionDatabase with compatibility for both script and package modes
try:
    # Try relative imports first (when imported as part of utilities package)
    from .LegionData import LegionDatabase
    from .LegionUtils import get_writable_path
except ImportError:
    try:
        # Try package imports (when running with MainMenu)
        from utilities.LegionData import LegionDatabase
        from utilities.LegionUtils import get_writable_path
    except ImportError:
        # Fallback to absolute imports (when running as standalone script)
        from LegionData import LegionDatabase
        from LegionUtils import get_writable_path

# =============================================================================
# TEIL 2: DIE BENUTZEROBERFLÄCHE (GUI) UND SPEICHER-LOGIK
# =============================================================================

class LegionArmyBuilder:
    def __init__(self, root):
        self.db = LegionDatabase()
        self.root = root
        self.root.title("SW Legion: Army Architect v4.0 (Save/Load)")
        self.root.geometry("1200x1100")

        # Tooltip-System initialisieren
        self.tooltip_window = None
        self.current_tooltip_widget = None

        logging.info("ArmeeBuilder initialized.")

        self.current_army_list = [] 
        self.current_faction = tk.StringVar()
        self.total_points = 0
        self.current_command_cards = []
        
        # Text-Display für Details
        self.selected_unit_text = tk.StringVar()
        
        # Kartenbild-Anzeige Variablen
        self.current_card_image = None
        self.current_card_image_path = None
        
        # Basis-Ordner für Speicherstände erstellen (beschreibbar)
        self.base_dir = get_writable_path("Armeen")
        logging.info(f"Using writable directory for armies: {self.base_dir}")

        self.setup_ui()
        self.setup_tooltips()

    def setup_tooltips(self):
        """Initialisiert das Tooltip-System für Hover-Texte"""
        self.tooltip_window = None
        
    def create_tooltip(self, widget, text):
        """Fügt einem Widget einen Hover-Tooltip hinzu"""
        def on_enter(event):
            self.show_tooltip(event, text)
        def on_leave(event):
            self.hide_tooltip()
            
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
    def show_tooltip(self, event, text):
        """Zeigt Tooltip an"""
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
                        wraplength=300, relief="solid", borderwidth=1,
                        padx=5, pady=3)
        label.pack()
        
    def hide_tooltip(self):
        """Versteckt Tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

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
        
        # Hover-Tooltips für Einheiten
        def show_unit_hover_tooltip(event):
            item = self.tree_units.identify_row(event.y)
            if item:
                values = self.tree_units.item(item, "values")
                if values:
                    unit_name = values[0]
                    faction = self.current_faction.get()
                    unit_data = next((u for u in self.db.units[faction] if u["name"] == unit_name), None)
                    
                    if unit_data and self.tooltip_window is None:
                        tooltip_text = self.format_unit_hover_tooltip(unit_data)
                        
                        x = event.x_root + 20
                        y = event.y_root + 20
                        
                        self.tooltip_window = tk.Toplevel(self.tree_units)
                        self.tooltip_window.wm_overrideredirect(True)
                        self.tooltip_window.geometry(f"+{x}+{y}")
                        
                        tooltip_frame = tk.Frame(self.tooltip_window, bg="lightyellow", 
                                               relief="solid", borderwidth=1)
                        tooltip_frame.pack()
                        
                        tooltip_label = tk.Label(tooltip_frame, text=tooltip_text, 
                                               bg="lightyellow", font=("Arial", 9), 
                                               wraplength=300, justify="left")
                        tooltip_label.pack(padx=5, pady=2)

        def hide_unit_hover_tooltip(event):
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None

        self.tree_units.bind("<Motion>", show_unit_hover_tooltip)
        self.tree_units.bind("<Leave>", hide_unit_hover_tooltip)
        self.tree_units.bind("<Button-1>", hide_unit_hover_tooltip)

        # 3. Info Box (erweitert für detaillierte Einheiten-Info)
        info_frame = tk.Frame(left_frame)
        info_frame.pack(fill="both", expand=True, pady=5)
        
        # Text-Widget für scrollbare Einheiten-Details
        self.txt_unit_details = tk.Text(info_frame, wrap="word", font=("Consolas", 9), 
                                       bg="#e1e1e1", relief=tk.SUNKEN, padx=10, pady=10)
        self.txt_unit_details.pack(fill="both", expand=True, side="left")
        
        # Scrollbar für Text-Widget
        scrollbar_details = ttk.Scrollbar(info_frame, orient="vertical", command=self.txt_unit_details.yview)
        scrollbar_details.pack(side="right", fill="y")
        self.txt_unit_details.config(yscrollcommand=scrollbar_details.set)
        
        # Initial-Text
        self.txt_unit_details.insert("1.0", "Wähle eine Einheit für Details...")
        self.txt_unit_details.config(state="disabled")
        
        # 3b. Kartenbild-Anzeige Frame
        self.card_image_frame = tk.LabelFrame(left_frame, text="📸 Kartenbild", font=("Segoe UI", 10, "bold"))
        self.card_image_frame.pack(fill="x", pady=5)
        
        # Canvas für Kartenbild
        self.card_image_canvas = tk.Canvas(self.card_image_frame, bg="#333", height=120, width=200)
        self.card_image_canvas.pack(pady=5, padx=5)
        
        # Placeholder für Kartenbild (wird von show_unit_stats aktualisiert)
        self.current_card_image = None
        self.card_image_label = tk.Label(self.card_image_frame, text="Kein Bild verknüpft", fg="gray")
        self.card_image_label.pack()
        
        # Button zum Vergrößern
        self.btn_enlarge_card = tk.Button(self.card_image_frame, text="🔍 Bild vergrößern", 
                                          command=self.show_enlarged_card_image, state="disabled")
        self.btn_enlarge_card.pack(pady=2)

        # 4. Hinzufügen Button
        btn_config = tk.Button(left_frame, text="Einheit anpassen & hinzufügen >", bg="#2196F3", fg="white", font=("Segoe UI", 11, "bold"), command=self.open_config_window)
        btn_config.pack(fill="x", pady=10)

        # 5. Kommandokarten Button
        self.btn_cards = tk.Button(left_frame, text="Kommandokarten wählen (0/7)", bg="#607D8B", fg="white", font=("Segoe UI", 10), command=self.open_deck_builder)
        self.btn_cards.pack(fill="x", pady=5)

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
        army_cols = ("ID", "Einheit", "Minis", "Upgrades", "Punkte")
        self.tree_army = ttk.Treeview(right_frame, columns=army_cols, show="headings")
        self.tree_army.heading("ID", text="#")
        self.tree_army.heading("Einheit", text="Einheit")
        self.tree_army.heading("Minis", text="Fig.")
        self.tree_army.heading("Upgrades", text="Ausrüstung")
        self.tree_army.heading("Punkte", text="Kosten")
        
        self.tree_army.column("ID", width=30, anchor="center")
        self.tree_army.column("Einheit", width=180)
        self.tree_army.column("Minis", width=40, anchor="center")
        self.tree_army.column("Upgrades", width=260)
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

        # Text-Display für Command Cards und Ausrüstung
        info_text_frame = tk.LabelFrame(right_frame, text="📖 Details", font=("Arial", 10, "bold"))
        info_text_frame.pack(fill="x", pady=10)
        
        self.txt_card_details = tk.Text(info_text_frame, wrap="word", font=("Arial", 9), 
                                       height=6, bg="#f9f9f9", relief=tk.SUNKEN)
        self.txt_card_details.pack(fill="x", padx=5, pady=5)
        
        scrollbar_card = ttk.Scrollbar(info_text_frame, orient="vertical", command=self.txt_card_details.yview)
        scrollbar_card.pack(side="right", fill="y")
        self.txt_card_details.config(yscrollcommand=scrollbar_card.set)
        
        # Initial-Text
        self.txt_card_details.insert("1.0", "Klicke auf Command Cards oder Ausrüstung für Details...")
        self.txt_card_details.config(state="disabled")

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
                "army": self.current_army_list,
                "command_cards": self.current_command_cards
            }
            
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=4, ensure_ascii=False)
                logging.info(f"Army saved to {file_path}")
                messagebox.showinfo("Erfolg", f"Armee erfolgreich gespeichert unter:\n{file_path}")
            except Exception as e:
                logging.error(f"Failed to save army: {e}")
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
                cards = data.get("command_cards", [])

                if faction and army_list is not None:
                    # 1. Fraktion setzen
                    self.current_faction.set(faction)
                    # 2. GUI Links aktualisieren (damit man Einheiten hinzufügen kann)
                    self.update_unit_list()
                    # 3. Armee setzen
                    self.current_army_list = army_list
                    self.current_command_cards = cards
                    self.btn_cards.config(text=f"Kommandokarten wählen ({len(cards)}/7)")
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
        if not selected: 
            self.txt_unit_details.config(state="normal")
            self.txt_unit_details.delete("1.0", "end")
            self.txt_unit_details.insert("1.0", "Wähle eine Einheit für Details...")
            self.txt_unit_details.config(state="disabled")
            self.clear_card_image()
            return
        
        vals = self.tree_units.item(selected, "values")
        name = vals[0]
        faction = self.current_faction.get()
        
        # Einheit in DB suchen
        unit_data = next((u for u in self.db.units[faction] if u["name"] == name), None)
        
        if unit_data:
            # Erstelle detaillierte Einheiten-Beschreibung
            detail_text = self.format_unit_details(unit_data)
            
            self.txt_unit_details.config(state="normal")
            self.txt_unit_details.delete("1.0", "end")
            self.txt_unit_details.insert("1.0", detail_text)
            self.txt_unit_details.config(state="disabled")
            
            # Kartenbild anzeigen
            self.display_unit_card_image(unit_data)

    def format_unit_details(self, unit_data):
        """Formatiert detaillierte Einheiten-Information für Text-Widget"""
        text = f"🎯 {unit_data['name']}\n"
        text += "=" * 40 + "\n\n"
        
        # Basis-Statistiken
        text += "📊 BASISWERTE:\n"
        text += f"❤️ Lebenspunkte: {unit_data.get('hp', 'N/A')}\n"
        text += f"⚔️ Mut: {unit_data.get('courage', 'N/A')}\n"
        text += f"🏃 Geschwindigkeit: {unit_data.get('speed', 'N/A')}\n"
        text += f"🛡️ Deckung: {unit_data.get('cover', 'N/A')}\n"
        text += f"👥 Miniaturen: {unit_data.get('minis', 'N/A')}\n"
        text += f"🏆 Rang: {unit_data.get('rank', 'N/A')}\n"
        text += f"💰 Kosten: {unit_data.get('points', 'N/A')} Punkte\n\n"
        
        # Ausrüstungsslots
        if 'slots' in unit_data and unit_data['slots']:
            text += "🎒 AUSRÜSTUNGSSLOTS:\n"
            for slot in unit_data['slots']:
                text += f"• {slot}\n"
            text += "\n"
        
        # Schlüsselwörter/Fähigkeiten
        if 'keywords' in unit_data and unit_data['keywords']:
            text += "⭐ SCHLÜSSELWÖRTER:\n"
            for keyword in unit_data['keywords']:
                text += f"• {keyword}\n"
            text += "\n"
        
        # Waffen
        if 'weapons' in unit_data and unit_data['weapons']:
            text += "⚔️ WAFFEN:\n"
            for weapon in unit_data['weapons']:
                if isinstance(weapon, dict):
                    weapon_name = weapon.get('name', 'Unbenannte Waffe')
                    weapon_range = weapon.get('range', 'N/A')
                    weapon_dice = weapon.get('dice', 'N/A')
                    text += f"• {weapon_name}\n"
                    text += f"  Reichweite: {weapon_range}\n"
                    text += f"  Würfel: {weapon_dice}\n"
                    if 'keywords' in weapon and weapon['keywords']:
                        text += f"  Keywords: {', '.join(weapon['keywords'])}\n"
                    text += "\n"
                else:
                    text += f"• {weapon}\n"
        
        # Beschreibung/Info
        if 'info' in unit_data and unit_data['info']:
            text += "ℹ️ BESCHREIBUNG:\n"
            text += f"{unit_data['info']}\n\n"
        
        # Zusätzliche Daten
        if 'text' in unit_data and unit_data['text']:
            text += "📜 REGELTEXT:\n"
            text += f"{unit_data['text']}\n\n"
        
        return text

    def display_unit_card_image(self, unit_data):
        """Zeigt das verknüpfte Kartenbild einer Einheit an"""
        if not PIL_AVAILABLE:
            self.card_image_label.config(text="PIL nicht verfügbar")
            self.btn_enlarge_card.config(state="disabled")
            return
        
        # Suche nach verknüpftem Bild
        card_image_path = unit_data.get("card_image")
        
        # Auch in custom_units suchen
        if not card_image_path:
            unit_id = unit_data.get("id")
            unit_name = unit_data.get("name")
            
            # Prüfe ob Bild existiert basierend auf ID oder Name
            possible_paths = [
                f"db/card_images/{unit_id}.png",
                f"db/card_images/{unit_name}.png",
                f"db/card_images/{str(unit_name).replace(' ', '_')}.png"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    card_image_path = path
                    break
        
        if card_image_path and os.path.exists(card_image_path):
            try:
                # Bild laden und für Canvas skalieren
                img = Image.open(card_image_path)
                
                # Skalieren auf Canvas-Größe (max 200x120)
                img.thumbnail((200, 120), Image.LANCZOS)
                
                self.current_card_image = ImageTk.PhotoImage(img)
                self.current_card_image_path = card_image_path
                
                # Canvas aktualisieren
                self.card_image_canvas.delete("all")
                self.card_image_canvas.create_image(
                    100, 60,  # Mitte des Canvas
                    image=self.current_card_image,
                    anchor="center"
                )
                
                self.card_image_label.config(text=f"📸 {os.path.basename(card_image_path)}")
                self.btn_enlarge_card.config(state="normal")
                
            except Exception as e:
                logging.error(f"Fehler beim Laden des Kartenbilds: {e}")
                self.clear_card_image()
        else:
            self.clear_card_image()

    def clear_card_image(self):
        """Löscht die Kartenbild-Anzeige"""
        self.card_image_canvas.delete("all")
        self.current_card_image = None
        self.current_card_image_path = None
        self.card_image_label.config(text="Kein Bild verknüpft")
        self.btn_enlarge_card.config(state="disabled")

    def show_enlarged_card_image(self):
        """Zeigt das Kartenbild in einem vergrößerten Fenster"""
        if not PIL_AVAILABLE or not hasattr(self, 'current_card_image_path') or not self.current_card_image_path:
            return
        
        if not os.path.exists(self.current_card_image_path):
            return
        
        try:
            # Neues Fenster für vergrößertes Bild
            enlarge_window = tk.Toplevel(self.root)
            enlarge_window.title("Kartenbild - Vergrößert")
            enlarge_window.geometry("800x600")
            enlarge_window.configure(bg="#333")
            
            # Bild laden in Originalgröße (max 750x550)
            img = Image.open(self.current_card_image_path)
            
            # Skalieren wenn nötig
            max_w, max_h = 750, 550
            if img.width > max_w or img.height > max_h:
                img.thumbnail((max_w, max_h), Image.LANCZOS)
            
            enlarged_img = ImageTk.PhotoImage(img)
            
            # Label für Bild
            lbl_img = tk.Label(enlarge_window, image=enlarged_img, bg="#333")
            lbl_img.image = enlarged_img  # Referenz halten
            lbl_img.pack(expand=True, pady=10)
            
            # Schließen-Button
            btn_close = tk.Button(enlarge_window, text="Schließen", command=enlarge_window.destroy,
                                bg="#f44336", fg="white", font=("Segoe UI", 10))
            btn_close.pack(pady=10)
            
        except Exception as e:
            logging.error(f"Fehler beim Vergrößern des Kartenbilds: {e}")
            messagebox.showerror("Fehler", f"Bild konnte nicht geladen werden: {e}")

    def create_tooltip(self, widget, text):
        """Erstellt ein Hover-Tooltip für ein Widget im Army Builder"""
        def show_tooltip(event):
            if self.tooltip_window:
                self.tooltip_window.destroy()
            
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + 20
            
            self.tooltip_window = tk.Toplevel(widget)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.geometry(f"+{x}+{y}")
            
            # Tooltip-Inhalt
            tooltip_frame = tk.Frame(self.tooltip_window, bg="lightyellow", 
                                   relief="solid", borderwidth=1)
            tooltip_frame.pack()
            
            tooltip_label = tk.Label(tooltip_frame, text=text, bg="lightyellow", 
                                   font=("Arial", 9), wraplength=350, justify="left")
            tooltip_label.pack(padx=5, pady=2)
            
            self.current_tooltip_widget = widget

        def hide_tooltip(event):
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None
            self.current_tooltip_widget = None

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
        widget.bind("<ButtonPress>", hide_tooltip)

    def format_upgrade_tooltip_text(self, upgrade_data):
        """Formatiert Ausrüstungs-Tooltip für Army Builder"""
        if not upgrade_data:
            return "Keine Ausrüstungsinformation verfügbar"
        
        tooltip_text = f"🎒 {upgrade_data.get('name', 'Unbekannt')}\n"
        tooltip_text += f"💰 Kosten: {upgrade_data.get('points', 'N/A')} Punkte\n"
        tooltip_text += f"🔧 Slot: {upgrade_data.get('slot', 'N/A')}\n\n"
        
        # Regeltext
        upgrade_text = upgrade_data.get('text', '')
        if upgrade_text:
            tooltip_text += f"📖 Effekt:\n{upgrade_text}\n"
        
        # Schlüsselwörter
        keywords = upgrade_data.get('keywords', [])
        if keywords:
            tooltip_text += f"\n⭐ Keywords: {', '.join(keywords)}"
        
        return tooltip_text
        
    def is_command_card_valid_for_army(self, command_card, army_unit_names, faction):
        """Prüft ob Command Card für die aktuelle Armee verfügbar ist"""
        if not command_card:
            return False
        
        # Immer verfügbare generische Command Cards (Standing Orders, etc.)
        generic_cards = ["Standing Orders", "Ambush", "Push", "Assault"]
        card_name = command_card.get('name', '')
        
        if card_name in generic_cards:
            return True
            
        # Prüfe auf Einheiten-spezifische Beschränkungen
        restricted_to = command_card.get('restricted_to_unit', [])
        if restricted_to:
            # Card ist nur für bestimmte Einheiten verfügbar
            for unit_id in restricted_to:
                # Finde Einheit im DB und prüfe Namen
                for unit in self.db.units.get(faction, []):
                    if (unit.get('id') == unit_id or unit.get('name') == unit_id) and unit.get('name') in army_unit_names:
                        return True
            return False
        
        # Prüfe auf Rang-Beschränkungen
        card_text = command_card.get('text', '').lower()
        
        # Kommandeur-spezifische Cards
        if 'commander' in card_text or 'kommandeur' in card_text:
            # Prüfe ob Kommandeur in Armee
            for unit_name in army_unit_names:
                unit_data = next((u for u in self.db.units.get(faction, []) if u.get('name') == unit_name), None)
                if unit_data and unit_data.get('rank') == 'Commander':
                    return True
            return False
        
        # Operative-spezifische Cards
        if 'operative' in card_text:
            for unit_name in army_unit_names:
                unit_data = next((u for u in self.db.units.get(faction, []) if u.get('name') == unit_name), None)
                if unit_data and unit_data.get('rank') == 'Operative':
                    return True
            return False
            
        # Standardmäßig alle anderen Cards verfügbar wenn keine spezifischen Beschränkungen
        return True

    def display_card_details(self, command_card):
        """Zeigt Command Card Details im Text-Widget an"""
        if not command_card:
            return
            
        self.txt_card_details.config(state="normal")
        self.txt_card_details.delete("1.0", "end")
        
        detail_text = f"📜 {command_card.get('name', 'Unbekannt')}\n"
        detail_text += "=" * 50 + "\n\n"
        
        # Basis-Info
        detail_text += f"🎯 Pips: {command_card.get('pips', 'N/A')}\n"
        
        # Beschränkungen
        restricted_to = command_card.get('restricted_to_unit', [])
        if restricted_to:
            detail_text += f"🔒 Beschränkt auf: {', '.join(restricted_to)}\n"
        
        detail_text += "\n📖 EFFEKT:\n"
        card_text = command_card.get('text', 'Kein Effekt-Text verfügbar')
        detail_text += f"{card_text}\n\n"
        
        # Keywords falls vorhanden
        keywords = command_card.get('keywords', [])
        if keywords:
            detail_text += f"⭐ Keywords: {', '.join(keywords)}\n\n"
        
        # Multi-Target Hinweis
        card_text_lower = card_text.lower()
        if any(keyword in card_text_lower for keyword in ['bis zu', 'all', 'alle', 'choose', 'wähle', 'multiple']):
            detail_text += "⚡ Diese Karte kann mehrere Ziele betreffen!\n"
        
        self.txt_card_details.insert("1.0", detail_text)
        self.txt_card_details.config(state="disabled")

    def display_upgrade_details(self, upgrade_data):
        """Zeigt Upgrade-Details im Text-Widget an"""
        if not upgrade_data:
            return
            
        self.txt_card_details.config(state="normal")
        self.txt_card_details.delete("1.0", "end")
        
        detail_text = f"🎒 {upgrade_data.get('name', 'Unbekannt')}\n"
        detail_text += "=" * 50 + "\n\n"
        
        # Basis-Info
        detail_text += f"💰 Kosten: {upgrade_data.get('points', 'N/A')} Punkte\n"
        detail_text += f"🔧 Slot: {upgrade_data.get('type', upgrade_data.get('slot', 'N/A'))}\n\n"
        
        # Effekt-Text - Prüfe sowohl 'text' als auch andere mögliche Felder
        upgrade_text = upgrade_data.get('text', '')
        if not upgrade_text:
            upgrade_text = upgrade_data.get('description', '')
        if not upgrade_text:
            upgrade_text = upgrade_data.get('effect', '')
            
        if upgrade_text:
            detail_text += "📖 EFFEKT:\n"
            detail_text += f"{upgrade_text}\n\n"
        
        # Waffen-Daten falls vorhanden
        if upgrade_data.get('type') == 'weapon' or 'weapon' in str(upgrade_data.get('slot', '')).lower():
            if 'range' in upgrade_data:
                detail_text += f"🎯 Reichweite: {upgrade_data.get('range', 'N/A')}\n"
            if 'dice' in upgrade_data:
                detail_text += f"🎲 Würfel: {upgrade_data.get('dice', 'N/A')}\n"
            if 'attack' in upgrade_data:
                detail_text += f"⚔️ Angriff: {upgrade_data.get('attack', 'N/A')}\n"
        
        # Schlüsselwörter
        keywords = upgrade_data.get('keywords', [])
        if keywords:
            detail_text += f"⭐ Keywords: {', '.join(keywords)}\n"
        
        # Beschränkungen
        restrictions = upgrade_data.get('restricted_to', [])
        if restrictions:
            detail_text += f"🔒 Beschränkt auf: {', '.join(restrictions)}\n"
            
        self.txt_card_details.insert("1.0", detail_text)
        self.txt_card_details.config(state="disabled")

    def format_unit_hover_tooltip(self, unit_data):
        """Formatiert kurze Unit-Info für Hover-Tooltip"""
        if not unit_data:
            return "Keine Einheiteninformation verfügbar"
        
        tooltip_text = f"🎯 {unit_data.get('name', 'Unbekannt')}\n"
        tooltip_text += f"💰 Kosten: {unit_data.get('points', 'N/A')} Punkte\n"
        tooltip_text += f"❤️ HP: {unit_data.get('hp', 'N/A')}\n"
        tooltip_text += f"⚔️ Mut: {unit_data.get('courage', 'N/A')}\n"
        tooltip_text += f"🏆 Rang: {unit_data.get('rank', 'N/A')}\n"
        
        # Kurze Info über Slots
        slots = unit_data.get('slots', [])
        if slots:
            tooltip_text += f"🎒 Slots: {len(slots)} ({', '.join(slots[:3])}{'...' if len(slots) > 3 else ''})\n"
        
        # Kurze Beschreibung wenn vorhanden
        info = unit_data.get('info', '')
        if info and len(info) < 100:
            tooltip_text += f"\n📖 {info}"
        elif info:
            tooltip_text += f"\n📖 {info[:97]}..."
        
        return tooltip_text

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
        top.geometry("800x750")
        
        tk.Label(top, text=f"Konfiguration: {unit_name}", font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        # Hauptcontainer mit zwei Bereichen
        main_container = tk.Frame(top)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Links: Ausrüstungsauswahl
        left_frame = tk.Frame(main_container)
        left_frame.pack(side="left", fill="both", expand=True)
        
        # Scrollbarer Bereich (Canvas) für viele Slots
        canvas = tk.Canvas(left_frame)
        scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Rechts: Text-Details
        right_frame = tk.LabelFrame(main_container, text="📖 Ausrüstungs-Details", font=("Arial", 10, "bold"))
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Text-Widget für Ausrüstungs-Details im Popup
        config_text_widget = tk.Text(right_frame, wrap="word", font=("Arial", 9), 
                                    bg="#f9f9f9", relief=tk.SUNKEN, width=40)
        config_text_widget.pack(fill="both", expand=True, padx=5, pady=5)
        
        config_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=config_text_widget.yview)
        config_scrollbar.pack(side="right", fill="y")
        config_text_widget.config(yscrollcommand=config_scrollbar.set)
        
        # Initial-Text
        config_text_widget.insert("1.0", "Wähle Ausrüstung aus den Dropdowns für Details...")
        config_text_widget.config(state="disabled")
        
        def display_upgrade_in_popup(upgrade_data):
            """Zeigt Upgrade-Details im Popup-Text-Widget an"""
            if not upgrade_data:
                return
                
            config_text_widget.config(state="normal")
            config_text_widget.delete("1.0", "end")
            
            detail_text = f"🎒 {upgrade_data.get('name', 'Unbekannt')}\n"
            detail_text += "=" * 40 + "\n\n"
            
            # Basis-Info
            detail_text += f"💰 Kosten: {upgrade_data.get('points', 'N/A')} Punkte\n"
            detail_text += f"🔧 Slot: {upgrade_data.get('type', upgrade_data.get('slot', 'N/A'))}\n\n"
            
            # Effekt-Text - Umfassende Suche
            upgrade_text = upgrade_data.get('text', '')
            if not upgrade_text:
                upgrade_text = upgrade_data.get('description', '')
            if not upgrade_text:
                upgrade_text = upgrade_data.get('effect', '')
                
            if upgrade_text:
                detail_text += "📖 EFFEKT:\n"
                detail_text += f"{upgrade_text}\n\n"
            
            # Waffen-Daten
            if upgrade_data.get('type') == 'weapon' or 'weapon' in str(upgrade_data.get('slot', '')).lower():
                if 'range' in upgrade_data:
                    detail_text += f"🎯 Reichweite: {upgrade_data.get('range', 'N/A')}\n"
                if 'dice' in upgrade_data:
                    detail_text += f"🎲 Würfel: {upgrade_data.get('dice', 'N/A')}\n"
                if 'attack' in upgrade_data:
                    detail_text += f"⚔️ Angriff: {upgrade_data.get('attack', 'N/A')}\n"
                if 'keywords' in upgrade_data:
                    detail_text += f"⚔️ Waffen-Keywords: {', '.join(upgrade_data.get('keywords', []))}\n"
            
            # Schlüsselwörter
            keywords = upgrade_data.get('keywords', [])
            if keywords:
                detail_text += f"⭐ Keywords: {', '.join(keywords)}\n"
            
            # Beschränkungen
            restrictions = upgrade_data.get('restricted_to', [])
            if restrictions:
                detail_text += f"🔒 Beschränkt auf: {', '.join(restrictions)}\n"
                
            config_text_widget.insert("1.0", detail_text)
            config_text_widget.config(state="disabled")

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
            
            # Tooltip für Combobox hinzufügen
            def create_upgrade_tooltip(combo_widget, upgrade_mapping):
                def show_upgrade_tooltip(event):
                    current_selection = combo_widget.get()
                    if current_selection and current_selection != "--- Leer ---":
                        upgrade_data = upgrade_mapping.get(current_selection)
                        if upgrade_data:
                            tooltip_text = self.format_upgrade_tooltip_text(upgrade_data)
                            if self.tooltip_window:
                                self.tooltip_window.destroy()
                            
                            x = combo_widget.winfo_rootx() + 20
                            y = combo_widget.winfo_rooty() + 20
                            
                            self.tooltip_window = tk.Toplevel(combo_widget)
                            self.tooltip_window.wm_overrideredirect(True)
                            self.tooltip_window.geometry(f"+{x}+{y}")
                            
                            tooltip_frame = tk.Frame(self.tooltip_window, bg="lightyellow", 
                                                   relief="solid", borderwidth=1)
                            tooltip_frame.pack()
                            
                            tooltip_label = tk.Label(tooltip_frame, text=tooltip_text, 
                                                   bg="lightyellow", font=("Arial", 9), 
                                                   wraplength=350, justify="left")
                            tooltip_label.pack(padx=5, pady=2)

                def hide_upgrade_tooltip(event):
                    if self.tooltip_window:
                        self.tooltip_window.destroy()
                        self.tooltip_window = None

                combo_widget.bind("<Enter>", show_upgrade_tooltip)
                combo_widget.bind("<Leave>", hide_upgrade_tooltip)
                combo_widget.bind("<<ComboboxSelected>>", hide_upgrade_tooltip)
                combo_widget.bind("<Button-1>", hide_upgrade_tooltip)
            
            create_upgrade_tooltip(cb, upgrade_map)
            
            # Event für Upgrade-Auswahl und Text-Display
            def on_upgrade_select(event, combo_widget=cb, mapping=upgrade_map):
                selected = combo_widget.get()
                if selected and selected != "--- Leer ---":
                    upgrade_data = mapping.get(selected)
                    if upgrade_data:
                        display_upgrade_in_popup(upgrade_data)
                else:
                    # Zeige Standard-Text wenn "Leer" ausgewählt
                    config_text_widget.config(state="normal")
                    config_text_widget.delete("1.0", "end")
                    config_text_widget.insert("1.0", "Wähle Ausrüstung aus den Dropdowns für Details...")
                    config_text_widget.config(state="disabled")
            
            cb.bind("<<ComboboxSelected>>", on_upgrade_select)
            cb.bind("<Button-1>", lambda e, combo=cb, mapping=upgrade_map: top.after(100, lambda: on_upgrade_select(None, combo, mapping)))
            
            selectors.append({"var": var, "map": upgrade_map})

        def add_confirmed():
            total_cost = unit_data["points"]
            chosen_upgrades_list = []
            # NEU: Extra Minis berechnen
            base_minis = unit_data.get("minis", 1)
            extra_minis = 0
            
            for sel in selectors:
                val = sel["var"].get()
                if val != "--- Leer ---":
                    upg_data = sel["map"][val]
                    total_cost += upg_data["points"]
                    chosen_upgrades_list.append(val) # Speichert "Name (Punkte)"
                    if upg_data.get("adds_mini"):
                        extra_minis += 1
            
            final_minis = base_minis + extra_minis

            # Zur Armee hinzufügen
            self.current_army_list.append({
                "name": unit_name,
                "upgrades": chosen_upgrades_list,
                "points": total_cost,
                "base_points": unit_data["points"],
                "minis": final_minis
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
            # Minis abrufen oder defaulten falls altes Savefile
            minis = unit.get("minis", "?")
            self.tree_army.insert("", "end", values=(idx+1, unit["name"], minis, upg_str, unit["points"]))
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

    def open_deck_builder(self):
        faction = self.current_faction.get()
        if not faction:
             messagebox.showwarning("Fehler", "Bitte wähle zuerst eine Fraktion.")
             return
             
        if not self.current_army_list:
             messagebox.showwarning("Info", "Füge zuerst Einheiten zur Armee hinzu, um passende Command Cards zu sehen.")
             return

        top = tk.Toplevel(self.root)
        top.title("Kommandokarten Hand (7 Karten)")
        top.geometry("1000x600")

        # Layout: Available (Left) -> Buttons -> Selected (Right)
        f_left = tk.LabelFrame(top, text="Verfügbare Karten")
        f_left.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        f_mid = tk.Frame(top)
        f_mid.pack(side="left", fill="y", padx=5)

        f_right = tk.LabelFrame(top, text=f"Gewählte Hand ({len(self.current_command_cards)}/7)")
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

        # Load Cards und filtere basierend auf Armee-Einheiten
        all_cards = self.db.get_command_cards(faction)
        valid_pool = []
        
        # Sammle alle Einheitennamen in der aktuellen Armee
        army_unit_names = [unit['name'] for unit in self.current_army_list]
        
        for c in all_cards:
            # Prüfe ob Command Card für die Armee verfügbar ist
            if self.is_command_card_valid_for_army(c, army_unit_names, faction):
                valid_pool.append(c)

        # Sort by pips
        valid_pool.sort(key=lambda x: x.get("pips", 0))

        for c in valid_pool:
            tv_avail.insert("", "end", values=(c["name"], c["pips"]), tags=(str(c),))
            
        # Event-Handler für Card-Selection und Text-Display
        def on_card_select(event):
            selection = event.widget.focus()
            if selection:
                item = event.widget.item(selection)
                card_name = item["values"][0]
                card = next((c for c in valid_pool if c["name"] == card_name), None)
                if card:
                    self.display_card_details(card)
                    
        def on_selected_card_select(event):
            selection = event.widget.focus()
            if selection:
                item = event.widget.item(selection)
                card_name = item["values"][0]
                card = next((c for c in temp_selected if c["name"] == card_name), None)
                if card:
                    self.display_card_details(card)
        
        tv_avail.bind("<<TreeviewSelect>>", on_card_select)
        tv_sel.bind("<<TreeviewSelect>>", on_selected_card_select)

        temp_selected = list(self.current_command_cards)

        def update_status():
            count = len(temp_selected)
            f_right.config(text=f"Gewählte Hand ({count}/7)")

            # Repopulate selection list
            for item in tv_sel.get_children(): tv_sel.delete(item)
            for c in temp_selected:
                tv_sel.insert("", "end", values=(c["name"], c["pips"]))

            # Check constraints
            pips = [c.get("pips", 0) for c in temp_selected]
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

            if len(temp_selected) >= 7: return
            # Check unique name in list
            if any(c["name"] == card["name"] for c in temp_selected): return

            temp_selected.append(card)
            update_status()

        def remove_card():
            sel = tv_sel.focus()
            if not sel: return
            item = tv_sel.item(sel)
            name = item["values"][0]

            # Remove by name
            for i, c in enumerate(temp_selected):
                if c["name"] == name:
                    del temp_selected[i]
                    break
            update_status()

        def confirm():
            self.current_command_cards = temp_selected
            self.btn_cards.config(text=f"Kommandokarten wählen ({len(temp_selected)}/7)")
            top.destroy()

        tk.Button(f_mid, text=">>", command=add_card).pack(pady=20)
        tk.Button(f_mid, text="<<", command=remove_card).pack(pady=20)

        lbl_status = tk.Label(top, text="...", font=("Segoe UI", 10, "bold"))
        lbl_status.pack(pady=10)

        btn_confirm = tk.Button(top, text="Speichern", command=confirm, state=tk.DISABLED, bg="#4CAF50", fg="white")
        btn_confirm.pack(pady=10)

        update_status()

# =============================================================================
# START
# =============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = LegionArmyBuilder(root)
    root.mainloop()