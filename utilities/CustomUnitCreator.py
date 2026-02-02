import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import uuid

# Import utilities with compatibility for both script and package modes
try:
    # Try relative imports first (when imported as part of utilities package)
    from .LegionUtils import get_data_path, get_writable_path
except ImportError:
    try:
        # Try package imports (when running with MainMenu)
        from utilities.LegionUtils import get_data_path, get_writable_path
    except ImportError:
        # Fallback to absolute imports (when running as standalone script)
        from LegionUtils import get_data_path, get_writable_path

class CustomUnitCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("SW Legion: Custom Unit Creator")
        self.root.geometry("900x800")

        self.custom_units_file = get_data_path("db/custom_units.json")
        self.units_data = self.load_data()

        self.setup_ui()

    def load_data(self):
        if not os.path.exists(self.custom_units_file):
            return []
        try:
            with open(self.custom_units_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Daten: {e}")
            return []

    def save_data(self):
        try:
            with open(self.custom_units_file, "w", encoding="utf-8") as f:
                json.dump(self.units_data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Erfolg", "Daten erfolgreich gespeichert!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

    def setup_ui(self):
        # Main Layout
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left Side: List of existing units
        left_frame = tk.Frame(main_frame, width=250, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(left_frame, text="Gespeicherte Einheiten", bg="#f0f0f0", font=("Segoe UI", 10, "bold")).pack(pady=10)

        self.unit_listbox = tk.Listbox(left_frame)
        self.unit_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.unit_listbox.bind("<<ListboxSelect>>", self.load_unit_into_form)

        btn_new = tk.Button(left_frame, text="Neue Einheit", command=self.clear_form)
        btn_new.pack(fill=tk.X, padx=5, pady=5)

        btn_delete = tk.Button(left_frame, text="Löschen", command=self.delete_unit, bg="#ffcccc")
        btn_delete.pack(fill=tk.X, padx=5, pady=5)

        self.refresh_listbox()

        # Right Side: Edit Form (Scrollable)
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(right_frame)
        scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.build_form(self.scrollable_frame)

    def build_form(self, parent):
        pad_y = 5

        # --- Basic Info ---
        lbl_title = tk.Label(parent, text="Einheit bearbeiten", font=("Segoe UI", 14, "bold"))
        lbl_title.grid(row=0, column=0, columnspan=4, pady=10, sticky="w")

        # Name
        tk.Label(parent, text="Name:").grid(row=1, column=0, sticky="e", padx=5, pady=pad_y)
        self.entry_name = tk.Entry(parent, width=30)
        self.entry_name.grid(row=1, column=1, sticky="w", padx=5, pady=pad_y)

        # Points
        tk.Label(parent, text="Punkte:").grid(row=1, column=2, sticky="e", padx=5, pady=pad_y)
        self.entry_points = tk.Entry(parent, width=10)
        self.entry_points.grid(row=1, column=3, sticky="w", padx=5, pady=pad_y)

        # Rank
        tk.Label(parent, text="Rang:").grid(row=2, column=0, sticky="e", padx=5, pady=pad_y)
        self.cb_rank = ttk.Combobox(parent, values=["Commander", "Operative", "Corps", "Special Forces", "Support", "Heavy"], state="readonly")
        self.cb_rank.grid(row=2, column=1, sticky="w", padx=5, pady=pad_y)
        self.cb_rank.current(0)

        # Subtitle / Unique (Optional, not strictly in internal model but good for UI)
        # We will map "Unique" to the "is_unique" flag if needed, or just part of name
        # For now, keep it simple to internal model.

        # HP / Courage / Speed
        tk.Label(parent, text="Lebenspunkte (HP):").grid(row=3, column=0, sticky="e", padx=5, pady=pad_y)
        self.entry_hp = tk.Entry(parent, width=10)
        self.entry_hp.grid(row=3, column=1, sticky="w", padx=5, pady=pad_y)

        tk.Label(parent, text="Mut (Courage):").grid(row=3, column=2, sticky="e", padx=5, pady=pad_y)
        self.entry_courage = tk.Entry(parent, width=10)
        self.entry_courage.grid(row=3, column=3, sticky="w", padx=5, pady=pad_y)

        tk.Label(parent, text="Geschwindigkeit:").grid(row=4, column=0, sticky="e", padx=5, pady=pad_y)
        self.entry_speed = tk.Entry(parent, width=10)
        self.entry_speed.grid(row=4, column=1, sticky="w", padx=5, pady=pad_y)

        tk.Label(parent, text="Minis:").grid(row=4, column=2, sticky="e", padx=5, pady=pad_y)
        self.entry_minis = tk.Entry(parent, width=10)
        self.entry_minis.insert(0, "1")
        self.entry_minis.grid(row=4, column=3, sticky="w", padx=5, pady=pad_y)

        # Defense
        tk.Label(parent, text="Verteidigungswürfel:").grid(row=5, column=0, sticky="e", padx=5, pady=pad_y)
        self.cb_defense = ttk.Combobox(parent, values=["Red", "White"], state="readonly")
        self.cb_defense.grid(row=5, column=1, sticky="w", padx=5, pady=pad_y)
        self.cb_defense.current(1)

        # Surges
        tk.Label(parent, text="Wogen (Surges):").grid(row=6, column=0, sticky="e", padx=5, pady=pad_y)

        self.var_surge_atk = tk.BooleanVar()
        self.var_surge_def = tk.BooleanVar()

        chk_atk = tk.Checkbutton(parent, text="Angriff: Krit", variable=self.var_surge_atk)
        chk_atk.grid(row=6, column=1, sticky="w", padx=5, pady=pad_y)

        chk_def = tk.Checkbutton(parent, text="Verteidigung: Block", variable=self.var_surge_def)
        chk_def.grid(row=6, column=2, columnspan=2, sticky="w", padx=5, pady=pad_y)

        # --- Factions ---
        tk.Label(parent, text="Fraktionen:", font=("Segoe UI", 10, "bold")).grid(row=7, column=0, sticky="nw", padx=5, pady=10)

        self.factions_vars = {}
        factions = ["Galaktisches Imperium", "Rebellenallianz", "Separatistenallianz", "Galaktische Republik", "Schattenkollektiv"]

        f_frame = tk.Frame(parent)
        f_frame.grid(row=7, column=1, columnspan=3, sticky="w")

        for f in factions:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(f_frame, text=f, variable=var)
            chk.pack(anchor="w")
            self.factions_vars[f] = var

        # --- Keywords ---
        tk.Label(parent, text="Einheiten-Keywords:", font=("Segoe UI", 10, "bold")).grid(row=8, column=0, sticky="nw", padx=5, pady=10)
        self.entry_keywords = tk.Entry(parent, width=60)
        self.entry_keywords.grid(row=8, column=1, columnspan=3, sticky="w", padx=5, pady=10)
        tk.Label(parent, text="(Kommagetrennt, z.B. 'Sprung 1, Ansturm')").grid(row=9, column=1, columnspan=3, sticky="w", padx=5)

        # --- Slots ---
        tk.Label(parent, text="Upgrade Slots:", font=("Segoe UI", 10, "bold")).grid(row=10, column=0, sticky="nw", padx=5, pady=10)

        self.slot_frame = tk.Frame(parent)
        self.slot_frame.grid(row=10, column=1, columnspan=3, sticky="w")

        self.slots_vars = [] # List of StringVars

        btn_add_slot = tk.Button(self.slot_frame, text="+ Slot", command=self.add_slot_ui)
        btn_add_slot.pack(side="top", anchor="w")

        self.slots_container = tk.Frame(self.slot_frame)
        self.slots_container.pack(fill="x", pady=5)

        # --- Weapons ---
        tk.Label(parent, text="Waffen:", font=("Segoe UI", 10, "bold")).grid(row=11, column=0, sticky="nw", padx=5, pady=10)

        self.weapon_frame = tk.Frame(parent)
        self.weapon_frame.grid(row=11, column=1, columnspan=3, sticky="w")

        btn_add_wep = tk.Button(self.weapon_frame, text="+ Waffe", command=self.add_weapon_ui)
        btn_add_wep.pack(side="top", anchor="w")

        self.weapons_container = tk.Frame(self.weapon_frame)
        self.weapons_container.pack(fill="x", pady=5)

        self.weapon_entries = [] # List of dicts with UI references

        # --- Action Buttons ---
        btn_save = tk.Button(parent, text="💾 Speichern", command=self.save_unit, bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold"))
        btn_save.grid(row=12, column=1, pady=30, sticky="w")

        self.current_unit_id = None # If editing, store UUID here

    def add_slot_ui(self, value=None):
        row_f = tk.Frame(self.slots_container)
        row_f.pack(fill="x", pady=2)

        var = tk.StringVar(value=value if value else "Training")
        cb = ttk.Combobox(row_f, textvariable=var, values=["Force", "Command", "Gear", "Training", "Comms", "Grenades", "Heavy Weapon", "Personnel", "Pilot", "Hardpoint", "Armament", "Generator", "Crew"], width=15)
        cb.pack(side="left")

        btn_del = tk.Button(row_f, text="X", command=lambda: self.remove_slot_ui(row_f, var), bg="#ffcccc", width=2)
        btn_del.pack(side="left", padx=5)

        self.slots_vars.append(var)

    def remove_slot_ui(self, frame, var):
        frame.destroy()
        if var in self.slots_vars:
            self.slots_vars.remove(var)

    def add_weapon_ui(self, data=None):
        # data = {"name": "", "range": [1,3], "dice": {"red":0...}, "keywords": []}
        w_frame = tk.Frame(self.weapons_container, relief=tk.RIDGE, bd=2, pady=5, padx=5)
        w_frame.pack(fill="x", pady=5)

        # Line 1: Name & Range
        l1 = tk.Frame(w_frame)
        l1.pack(fill="x")
        tk.Label(l1, text="Name:").pack(side="left")
        entry_name = tk.Entry(l1, width=20)
        entry_name.pack(side="left", padx=5)

        tk.Label(l1, text="Reichweite:").pack(side="left", padx=5)
        entry_min = tk.Entry(l1, width=2)
        entry_min.pack(side="left")
        tk.Label(l1, text="-").pack(side="left")
        entry_max = tk.Entry(l1, width=2)
        entry_max.pack(side="left")

        btn_del = tk.Button(l1, text="X", bg="#ffcccc", command=lambda: self.remove_weapon_ui(w_frame, entry_name))
        btn_del.pack(side="right")

        # Line 2: Dice
        l2 = tk.Frame(w_frame)
        l2.pack(fill="x", pady=2)
        tk.Label(l2, text="Würfel (Rot/Schwarz/Weiß):").pack(side="left")
        entry_red = tk.Entry(l2, width=3)
        entry_red.pack(side="left", padx=2)
        entry_black = tk.Entry(l2, width=3)
        entry_black.pack(side="left", padx=2)
        entry_white = tk.Entry(l2, width=3)
        entry_white.pack(side="left", padx=2)

        # Line 3: Keywords
        l3 = tk.Frame(w_frame)
        l3.pack(fill="x", pady=2)
        tk.Label(l3, text="Keywords:").pack(side="left")
        entry_kw = tk.Entry(l3, width=40)
        entry_kw.pack(side="left", padx=5)

        # Defaults / Load Data
        if data:
            entry_name.insert(0, data.get("name", ""))
            rng = data.get("range", [0, 0])
            entry_min.insert(0, str(rng[0]))
            entry_max.insert(0, str(rng[1]))
            dice = data.get("dice", {})
            entry_red.insert(0, str(dice.get("red", 0)))
            entry_black.insert(0, str(dice.get("black", 0)))
            entry_white.insert(0, str(dice.get("white", 0)))

            # Keywords list to string
            kws = data.get("keywords", [])
            entry_kw.insert(0, ", ".join(kws))
        else:
            entry_min.insert(0, "1")
            entry_max.insert(0, "3")
            entry_red.insert(0, "0")
            entry_black.insert(0, "0")
            entry_white.insert(0, "0")

        # Store references
        ref = {
            "frame": w_frame,
            "name": entry_name,
            "min": entry_min,
            "max": entry_max,
            "red": entry_red,
            "black": entry_black,
            "white": entry_white,
            "kw": entry_kw
        }
        self.weapon_entries.append(ref)

        # Update delete command to remove from list
        btn_del.config(command=lambda: self.remove_weapon_ui(w_frame, ref))

    def remove_weapon_ui(self, frame, ref):
        frame.destroy()
        if ref in self.weapon_entries:
            self.weapon_entries.remove(ref)

    def refresh_listbox(self):
        self.unit_listbox.delete(0, tk.END)
        for u in self.units_data:
            name = u.get("unit_data", {}).get("name", "Unbenannt")
            self.unit_listbox.insert(tk.END, name)

    def clear_form(self):
        self.current_unit_id = None
        self.entry_name.delete(0, tk.END)
        self.entry_points.delete(0, tk.END)
        self.entry_hp.delete(0, tk.END)
        self.entry_courage.delete(0, tk.END)
        self.entry_speed.delete(0, tk.END)
        self.entry_minis.delete(0, tk.END)
        self.entry_minis.insert(0, "1")
        self.entry_keywords.delete(0, tk.END)

        self.cb_rank.current(0)
        self.cb_defense.current(1)
        self.var_surge_atk.set(False)
        self.var_surge_def.set(False)

        for k in self.factions_vars:
            self.factions_vars[k].set(False)

        # Clear slots
        for child in self.slots_container.winfo_children():
            child.destroy()
        self.slots_vars = []

        # Clear weapons
        for child in self.weapons_container.winfo_children():
            child.destroy()
        self.weapon_entries = []

    def load_unit_into_form(self, event):
        sel = self.unit_listbox.curselection()
        if not sel: return

        idx = sel[0]
        data = self.units_data[idx]
        u = data.get("unit_data", {})

        self.clear_form()
        self.current_unit_id = data.get("id")

        self.entry_name.insert(0, u.get("name", ""))
        self.entry_points.insert(0, str(u.get("points", 0)))
        self.entry_hp.insert(0, str(u.get("hp", 1)))
        self.entry_courage.insert(0, str(u.get("courage", "-")))
        self.entry_speed.insert(0, str(u.get("speed", 0)))
        self.entry_minis.delete(0, tk.END)
        self.entry_minis.insert(0, str(u.get("minis", 1)))
        self.entry_keywords.insert(0, u.get("info", ""))

        self.cb_rank.set(u.get("rank", "Corps"))

        self.cb_defense.set(u.get("defense", "White"))

        surges = u.get("surge", {})
        if surges.get("attack") == "crit": self.var_surge_atk.set(True)
        if surges.get("defense") == "block": self.var_surge_def.set(True)

        # Factions
        factions = data.get("factions", [])
        for f in factions:
            if f in self.factions_vars:
                self.factions_vars[f].set(True)

        # Slots
        for s in u.get("slots", []):
            self.add_slot_ui(s)

        # Weapons
        for w in u.get("weapons", []):
            self.add_weapon_ui(w)

    def delete_unit(self):
        sel = self.unit_listbox.curselection()
        if not sel: return

        if messagebox.askyesno("Löschen", "Einheit wirklich löschen?"):
            idx = sel[0]
            del self.units_data[idx]
            self.save_data()
            self.refresh_listbox()
            self.clear_form()

    def save_unit(self):
        # Validation
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("Fehler", "Name darf nicht leer sein!")
            return

        try:
            points = int(self.entry_points.get())
            hp = int(self.entry_hp.get())
            speed = int(self.entry_speed.get())
            minis = int(self.entry_minis.get())
        except ValueError:
            messagebox.showwarning("Fehler", "Punkte, HP, Minis und Geschwindigkeit müssen Zahlen sein.")
            return

        courage = self.entry_courage.get().strip()
        if courage == "": courage = "-"

        # Collect Factions
        selected_factions = [f for f, var in self.factions_vars.items() if var.get()]
        if not selected_factions:
            messagebox.showwarning("Fehler", "Mindestens eine Fraktion auswählen!")
            return

        # Collect Slots
        slots = [var.get() for var in self.slots_vars]

        # Collect Weapons
        weapons = []
        for w in self.weapon_entries:
            w_name = w["name"].get().strip()
            if not w_name: continue

            try:
                mn = int(w["min"].get())
                mx = int(w["max"].get())
                dr = int(w["red"].get())
                db = int(w["black"].get())
                dw = int(w["white"].get())
            except ValueError:
                messagebox.showwarning("Fehler", "Waffenwerte müssen Zahlen sein.")
                return

            kws = [k.strip() for k in w["kw"].get().split(",") if k.strip()]

            weapons.append({
                "name": w_name,
                "range": [mn, mx],
                "dice": {"red": dr, "black": db, "white": dw},
                "keywords": kws
            })

        # Build Unit Dict
        unit_dict = {
            "name": name,
            "points": points,
            "rank": self.cb_rank.get(),
            "hp": hp,
            "courage": courage,
            "slots": slots,
            "info": self.entry_keywords.get(),
            "minis": minis,
            "speed": speed,
            "defense": self.cb_defense.get(),
            "surge": {
                "attack": "crit" if self.var_surge_atk.get() else None,
                "defense": "block" if self.var_surge_def.get() else None
            },
            "weapons": weapons,
            "id": str(uuid.uuid4()) # New ID if strictly new
        }

        # Structure for file
        entry = {
            "id": self.current_unit_id if self.current_unit_id else unit_dict["id"],
            "factions": selected_factions,
            "unit_data": unit_dict
        }

        # Update or Append
        found = False
        if self.current_unit_id:
            for i, u in enumerate(self.units_data):
                if u.get("id") == self.current_unit_id:
                    # Preserve ID
                    entry["id"] = self.current_unit_id
                    entry["unit_data"]["id"] = self.current_unit_id
                    self.units_data[i] = entry
                    found = True
                    break

        if not found:
            self.units_data.append(entry)
            self.current_unit_id = entry["id"]

        self.save_data()
        self.refresh_listbox()
        messagebox.showinfo("Gespeichert", f"Einheit '{name}' gespeichert.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomUnitCreator(root)
    root.mainloop()
