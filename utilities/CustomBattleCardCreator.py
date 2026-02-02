import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import uuid
from .LegionUtils import get_data_path

class CustomBattleCardCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("SW Legion: Custom Battle Card Creator")
        self.root.geometry("1100x700")

        self.custom_file = get_data_path("db/custom_battle_cards.json")
        self.maps_dir = "maps"
        if not os.path.exists(self.maps_dir):
            os.makedirs(self.maps_dir)

        self.cards_data = self.load_data()

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
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.custom_file), exist_ok=True)
            with open(self.custom_file, "w", encoding="utf-8") as f:
                json.dump(self.cards_data, f, indent=4, ensure_ascii=False)
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

        tk.Label(left_frame, text="Gespeicherte Karten", bg="#f0f0f0", font=("Segoe UI", 10, "bold")).pack(pady=10)

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

        tk.Label(right_frame, text="Schlachtkarte bearbeiten", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

        # Name
        tk.Label(right_frame, text="Name:").grid(row=1, column=0, sticky="e", pady=5)
        self.entry_name = tk.Entry(right_frame, width=40)
        self.entry_name.grid(row=1, column=1, sticky="w", pady=5)

        # Category
        tk.Label(right_frame, text="Kategorie:").grid(row=2, column=0, sticky="e", pady=5)
        self.cb_category = ttk.Combobox(right_frame, values=["Objective", "Deployment", "Condition"], state="readonly", width=20)
        self.cb_category.grid(row=2, column=1, sticky="w", pady=5)
        self.cb_category.current(0)
        self.cb_category.bind("<<ComboboxSelected>>", self.toggle_map_editor)

        # Text
        tk.Label(right_frame, text="Regeltext:").grid(row=3, column=0, sticky="ne", pady=5)
        self.txt_info = tk.Text(right_frame, width=40, height=5)
        self.txt_info.grid(row=3, column=1, sticky="w", pady=5)

        # Map Editor Frame (Initially hidden)
        self.map_frame = tk.Frame(right_frame, bd=2, relief=tk.GROOVE)
        self.map_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="w")

        tk.Label(self.map_frame, text="Aufstellungszonen zeichnen", font=("Segoe UI", 10, "bold")).pack(pady=5)

        tool_bar = tk.Frame(self.map_frame)
        tool_bar.pack(fill=tk.X)

        tk.Button(tool_bar, text="Rot Zone (Rechteck)", bg="#ffcdd2", command=lambda: self.set_tool("red")).pack(side=tk.LEFT, padx=5)
        tk.Button(tool_bar, text="Blau Zone (Rechteck)", bg="#bbdefb", command=lambda: self.set_tool("blue")).pack(side=tk.LEFT, padx=5)
        tk.Button(tool_bar, text="Löschen", bg="#ffcccc", command=self.clear_canvas).pack(side=tk.RIGHT, padx=5)

        # Canvas 6x3 ratio (approx 600x300)
        self.canvas = tk.Canvas(self.map_frame, width=600, height=300, bg="#e1f5fe")
        self.canvas.pack(pady=5)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Save Button
        btn_save = tk.Button(right_frame, text="💾 Speichern", command=self.save_entry, bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold"))
        btn_save.grid(row=5, column=1, pady=30, sticky="w")

        self.current_id = None
        self.current_tool = None
        self.current_shape = None
        self.map_items = [] # Store rect data: {"coords": [x0,y0,x1,y1], "color": "red"/"blue"}

        self.toggle_map_editor()

    def toggle_map_editor(self, event=None):
        cat = self.cb_category.get()
        if cat == "Deployment":
            self.map_frame.grid()
        else:
            self.map_frame.grid_remove()

    def set_tool(self, color):
        self.current_tool = color

    def clear_canvas(self):
        self.canvas.delete("all")
        self.map_items = []

    def on_press(self, event):
        if not self.current_tool: return
        self.start_x = event.x
        self.start_y = event.y
        color = "red" if self.current_tool == "red" else "blue"
        fill = "#ffcdd2" if color == "red" else "#bbdefb"

        self.current_shape = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            fill=fill, outline=color, tags="zone"
        )

    def on_drag(self, event):
        if self.current_shape:
            self.canvas.coords(self.current_shape, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        if self.current_shape:
            coords = self.canvas.coords(self.current_shape)
            # Normalize coords
            x0, y0, x1, y1 = coords
            if x0 > x1: x0, x1 = x1, x0
            if y0 > y1: y0, y1 = y1, y0

            self.map_items.append({
                "coords": [x0, y0, x1, y1],
                "color": self.current_tool
            })
            self.current_shape = None

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for entry in self.cards_data:
            name = entry.get("name", "Unbenannt")
            cat = entry.get("category", "?")[0].upper() # O/D/C
            self.listbox.insert(tk.END, f"[{cat}] {name}")

    def clear_form(self):
        self.current_id = None
        self.entry_name.delete(0, tk.END)
        self.cb_category.current(0)
        self.txt_info.delete("1.0", tk.END)
        self.clear_canvas()
        self.toggle_map_editor()

    def load_into_form(self, event):
        sel = self.listbox.curselection()
        if not sel: return

        idx = sel[0]
        data = self.cards_data[idx]

        self.clear_form()
        self.current_id = data.get("id")

        self.entry_name.insert(0, data.get("name", ""))
        self.cb_category.set(data.get("category", "Objective"))
        self.txt_info.insert("1.0", data.get("text", ""))
        self.toggle_map_editor()

        # Load Map if exists
        map_file = data.get("map_file")
        if map_file and os.path.exists(map_file):
            with open(map_file, "r") as f:
                items = json.load(f)
                self.map_items = items
                for item in items:
                    c = item["color"]
                    fill = "#ffcdd2" if c == "red" else "#bbdefb"
                    outline = "red" if c == "red" else "blue"
                    self.canvas.create_rectangle(*item["coords"], fill=fill, outline=outline, tags="zone")

    def delete_entry(self):
        sel = self.listbox.curselection()
        if not sel: return

        if messagebox.askyesno("Löschen", "Wirklich löschen?"):
            idx = sel[0]
            del self.cards_data[idx]
            self.save_data()
            self.refresh_listbox()
            self.clear_form()

    def save_entry(self):
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("Fehler", "Name fehlt!")
            return

        category = self.cb_category.get()
        text = self.txt_info.get("1.0", tk.END).strip()

        card_uuid = self.current_id if self.current_id else str(uuid.uuid4())

        # Save Map Data if Deployment
        map_file_path = None
        if category == "Deployment" and self.map_items:
            filename = f"{card_uuid}.json"
            map_file_path = os.path.join(self.maps_dir, filename)
            with open(map_file_path, "w") as f:
                json.dump(self.map_items, f)

        new_entry = {
            "name": name,
            "category": category,
            "text": text,
            "id": card_uuid,
            "is_custom": True,
            "map_file": map_file_path
        }

        # Update or Append
        if self.current_id:
            for i, entry in enumerate(self.cards_data):
                if entry.get("id") == self.current_id:
                    # Preserve map file if not updated? No, we overwrite it.
                    self.cards_data[i] = new_entry
                    break
        else:
            self.cards_data.append(new_entry)
            self.current_id = new_entry["id"]

        self.save_data()
        self.refresh_listbox()

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomBattleCardCreator(root)
    root.mainloop()
