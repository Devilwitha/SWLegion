import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import uuid

class CustomUpgradeCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("SW Legion: Custom Upgrade Creator")
        self.root.geometry("850x700")

        self.custom_file = "db/custom_upgrades.json"
        self.upgrades_data = self.load_data()

        self.setup_ui()

    def load_data(self):
        if not os.path.exists(self.custom_file):
            return []
        try:
            with open(self.custom_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Daten: {e}")
            return []

    def save_data(self):
        try:
            with open(self.custom_file, "w", encoding="utf-8") as f:
                json.dump(self.upgrades_data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Erfolg", "Daten erfolgreich gespeichert!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

    def setup_ui(self):
        # Main Layout
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left Side: List
        left_frame = tk.Frame(main_frame, width=250, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(left_frame, text="Gespeicherte Ausrüstung", bg="#f0f0f0", font=("Segoe UI", 10, "bold")).pack(pady=10)

        self.listbox = tk.Listbox(left_frame)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.load_into_form)

        btn_new = tk.Button(left_frame, text="Neu", command=self.clear_form)
        btn_new.pack(fill=tk.X, padx=5, pady=5)

        btn_delete = tk.Button(left_frame, text="Löschen", command=self.delete_entry, bg="#ffcccc")
        btn_delete.pack(fill=tk.X, padx=5, pady=5)

        self.refresh_listbox()

        # Right Side: Form
        right_frame = tk.Frame(main_frame, padx=20, pady=20)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(right_frame, text="Ausrüstung bearbeiten", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

        # Name
        tk.Label(right_frame, text="Name:").grid(row=1, column=0, sticky="e", pady=5)
        self.entry_name = tk.Entry(right_frame, width=40)
        self.entry_name.grid(row=1, column=1, sticky="w", pady=5)

        # Points
        tk.Label(right_frame, text="Punkte:").grid(row=2, column=0, sticky="e", pady=5)
        self.entry_points = tk.Entry(right_frame, width=10)
        self.entry_points.grid(row=2, column=1, sticky="w", pady=5)

        # Type
        tk.Label(right_frame, text="Typ:").grid(row=3, column=0, sticky="e", pady=5)
        types = ["Gear", "Force", "Command", "Training", "Comms", "Grenades", "Heavy Weapon", "Personnel", "Pilot", "Hardpoint", "Armament", "Generator", "Crew"]
        self.cb_type = ttk.Combobox(right_frame, values=types, state="readonly", width=20)
        self.cb_type.grid(row=3, column=1, sticky="w", pady=5)
        self.cb_type.current(0)

        # Adds Mini
        self.var_adds_mini = tk.BooleanVar()
        chk_mini = tk.Checkbutton(right_frame, text="Fügt Miniatur hinzu", variable=self.var_adds_mini)
        chk_mini.grid(row=4, column=1, sticky="w", pady=5)

        # Restriction: Unit Name
        tk.Label(right_frame, text="Nur für Einheit (Name):").grid(row=5, column=0, sticky="e", pady=5)
        self.entry_res_unit = tk.Entry(right_frame, width=40)
        self.entry_res_unit.grid(row=5, column=1, sticky="w", pady=5)
        tk.Label(right_frame, text="(Leer lassen für keine Einschränkung)", font=("Segoe UI", 8)).grid(row=6, column=1, sticky="w")

        # Restriction: Factions
        tk.Label(right_frame, text="Nur für Fraktionen:").grid(row=7, column=0, sticky="ne", pady=5)

        self.factions_vars = {}
        factions = ["Galaktisches Imperium", "Rebellenallianz", "Separatistenallianz", "Galaktische Republik", "Schattenkollektiv", "Dunkle Seite", "Helle Seite"]

        f_frame = tk.Frame(right_frame)
        f_frame.grid(row=7, column=1, sticky="w")

        for f in factions:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(f_frame, text=f, variable=var)
            chk.pack(anchor="w")
            self.factions_vars[f] = var

        # Text/Keywords
        tk.Label(right_frame, text="Text / Keywords:").grid(row=8, column=0, sticky="ne", pady=5)
        self.txt_info = tk.Text(right_frame, width=40, height=5)
        self.txt_info.grid(row=8, column=1, sticky="w", pady=5)

        # Save Button
        btn_save = tk.Button(right_frame, text="💾 Speichern", command=self.save_entry, bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold"))
        btn_save.grid(row=9, column=1, pady=30, sticky="w")

        self.current_id = None

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for entry in self.upgrades_data:
            name = entry.get("name", "Unbenannt")
            typ = entry.get("type", "?")
            self.listbox.insert(tk.END, f"[{typ}] {name}")

    def clear_form(self):
        self.current_id = None
        self.entry_name.delete(0, tk.END)
        self.entry_points.delete(0, tk.END)
        self.cb_type.current(0)
        self.entry_res_unit.delete(0, tk.END)
        self.txt_info.delete("1.0", tk.END)
        self.var_adds_mini.set(False)
        for k in self.factions_vars:
            self.factions_vars[k].set(False)

    def load_into_form(self, event):
        sel = self.listbox.curselection()
        if not sel: return

        idx = sel[0]
        data = self.upgrades_data[idx]

        self.clear_form()
        self.current_id = data.get("id")

        self.entry_name.insert(0, data.get("name", ""))
        self.entry_points.insert(0, str(data.get("points", 0)))
        self.cb_type.set(data.get("type", "Gear"))
        self.var_adds_mini.set(data.get("adds_mini", False))

        # Info text (might not exist in upgrade object strictly, usually only name/points matter for builder logic, but nice for printing)
        # We store it in "text"
        self.txt_info.insert("1.0", data.get("text", ""))

        # Restrictions
        restrictions = data.get("restricted_to", [])
        if restrictions:
            # Check unit name (simple check if not in factions list)
            known_factions = self.factions_vars.keys()
            unit_res = [r for r in restrictions if r not in known_factions]

            if unit_res:
                self.entry_res_unit.insert(0, unit_res[0]) # Support single unit restriction for now

            for r in restrictions:
                if r in self.factions_vars:
                    self.factions_vars[r].set(True)

    def delete_entry(self):
        sel = self.listbox.curselection()
        if not sel: return

        if messagebox.askyesno("Löschen", "Wirklich löschen?"):
            idx = sel[0]
            del self.upgrades_data[idx]
            self.save_data()
            self.refresh_listbox()
            self.clear_form()

    def save_entry(self):
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("Fehler", "Name fehlt!")
            return

        try:
            points = int(self.entry_points.get())
        except ValueError:
            messagebox.showwarning("Fehler", "Punkte müssen eine Zahl sein.")
            return

        typ = self.cb_type.get()
        text = self.txt_info.get("1.0", tk.END).strip()
        adds_mini = self.var_adds_mini.get()

        # Build Restrictions List
        restrictions = []

        # Factions
        for f, var in self.factions_vars.items():
            if var.get():
                restrictions.append(f)

        # Unit Name
        unit_res = self.entry_res_unit.get().strip()
        if unit_res:
            restrictions.append(unit_res)

        if not restrictions:
            restrictions = None

        new_entry = {
            "name": name,
            "type": typ,
            "points": points,
            "text": text,
            "restricted_to": restrictions,
            "adds_mini": adds_mini,
            "id": str(uuid.uuid4()),
            "is_custom": True
        }

        # Update or Append
        if self.current_id:
            for i, entry in enumerate(self.upgrades_data):
                if entry.get("id") == self.current_id:
                    new_entry["id"] = self.current_id
                    self.upgrades_data[i] = new_entry
                    break
        else:
            self.upgrades_data.append(new_entry)
            self.current_id = new_entry["id"]

        self.save_data()
        self.refresh_listbox()

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomUpgradeCreator(root)
    root.mainloop()
