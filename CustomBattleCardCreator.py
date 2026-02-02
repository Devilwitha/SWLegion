import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import uuid

class CustomBattleCardCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("SW Legion: Custom Battle Card Creator")
        self.root.geometry("800x600")

        self.custom_file = "custom_battle_cards.json"
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

        # Text
        tk.Label(right_frame, text="Regeltext:").grid(row=3, column=0, sticky="ne", pady=5)
        self.txt_info = tk.Text(right_frame, width=40, height=10)
        self.txt_info.grid(row=3, column=1, sticky="w", pady=5)

        # Save Button
        btn_save = tk.Button(right_frame, text="💾 Speichern", command=self.save_entry, bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold"))
        btn_save.grid(row=4, column=1, pady=30, sticky="w")

        self.current_id = None

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

        new_entry = {
            "name": name,
            "category": category,
            "text": text,
            "id": str(uuid.uuid4()),
            "is_custom": True
        }

        # Update or Append
        if self.current_id:
            for i, entry in enumerate(self.cards_data):
                if entry.get("id") == self.current_id:
                    new_entry["id"] = self.current_id
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
