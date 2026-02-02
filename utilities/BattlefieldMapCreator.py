import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, colorchooser
import json
import os
from PIL import Image, ImageDraw

# Import get_writable_path with compatibility for both script and package modes
try:
    # Try relative imports first (when imported as part of utilities package)
    from .LegionUtils import get_writable_path
except ImportError:
    try:
        # Try package imports (when running with MainMenu)
        from utilities.LegionUtils import get_writable_path
    except ImportError:
        # Fallback to absolute imports (when running as standalone script)
        from LegionUtils import get_writable_path

class BattlefieldMapCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("SW Legion: Battlefield Map Creator")
        self.root.geometry("1100x800")

        self.canvas_width = 800
        self.canvas_height = 533 # Approx 6x4 ratio (e.g. 150px per foot) -> 900x600 fits better on screen?
        # Let's say 1 foot = 120 pixels. 6ft = 720px. 3ft (Standard) = 360px.
        # Standard table 6x3ft.
        self.px_per_foot = 120
        self.canvas_width = 6 * self.px_per_foot
        self.canvas_height = 3 * self.px_per_foot

        self.shapes = [] # List of dicts: type, coords, color, label
        self.current_shape = None
        self.start_x = 0
        self.start_y = 0
        self.mode = "select" # select, rect, circle

        self.setup_ui()

    def setup_ui(self):
        # Toolbar
        toolbar = tk.Frame(self.root, bg="#ddd", pady=5)
        toolbar.pack(fill=tk.X)

        tk.Button(toolbar, text="Auswählen/Verschieben", command=lambda: self.set_mode("select")).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Rechteck", command=lambda: self.set_mode("rect")).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Kreis", command=lambda: self.set_mode("circle")).pack(side=tk.LEFT, padx=5)

        tk.Button(toolbar, text="Farbe", command=self.choose_color).pack(side=tk.LEFT, padx=20)
        tk.Button(toolbar, text="Text Label", command=self.add_label).pack(side=tk.LEFT, padx=5)

        tk.Button(toolbar, text="Löschen", command=self.delete_selected, bg="#ffcccc").pack(side=tk.LEFT, padx=20)

        tk.Button(toolbar, text="Bild Export", command=self.export_image, bg="#4CAF50", fg="white").pack(side=tk.RIGHT, padx=10)
        tk.Button(toolbar, text="Speichern", command=self.save_map, bg="#2196F3", fg="white").pack(side=tk.RIGHT, padx=5)
        tk.Button(toolbar, text="Laden", command=self.load_map, bg="#FF9800", fg="white").pack(side=tk.RIGHT, padx=5)

        # Canvas Area
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="#8FBC8F") # DarkSeaGreen
        self.canvas.pack(pady=20)

        # Draw Grid (1ft squares)
        for i in range(1, 6):
            x = i * self.px_per_foot
            self.canvas.create_line(x, 0, x, self.canvas_height, fill="#666", dash=(4, 4))
        for i in range(1, 3):
            y = i * self.px_per_foot
            self.canvas.create_line(0, y, self.canvas_width, y, fill="#666", dash=(4, 4))

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.status_lbl = tk.Label(self.root, text="Modus: Auswählen", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_lbl.pack(side=tk.BOTTOM, fill=tk.X)

        self.current_color = "#8B4513" # SaddleBrown default
        self.selected_item = None

    def set_mode(self, mode):
        self.mode = mode
        self.status_lbl.config(text=f"Modus: {mode.title()}")
        self.selected_item = None

    def choose_color(self):
        color = colorchooser.askcolor(title="Geländefarbe wählen")[1]
        if color:
            self.current_color = color

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

        if self.mode == "select":
            # Find closest
            item = self.canvas.find_closest(event.x, event.y)
            tags = self.canvas.gettags(item)
            if "shape" in tags:
                self.selected_item = item[0]
                self.drag_data = {"x": event.x, "y": event.y}
            else:
                self.selected_item = None
        elif self.mode in ["rect", "circle"]:
            self.current_shape = self.canvas.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y,
                fill=self.current_color, outline="black", tags="shape"
            )
            if self.mode == "circle":
                 self.canvas.itemconfig(self.current_shape, outline="black") # Placeholder, will reshape on drag

    def on_drag(self, event):
        if self.mode == "select" and self.selected_item:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.selected_item, dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

        elif self.mode == "rect":
            self.canvas.coords(self.current_shape, self.start_x, self.start_y, event.x, event.y)

        elif self.mode == "circle":
            self.canvas.coords(self.current_shape, self.start_x, self.start_y, event.x, event.y)
            # Actually make it an oval
            # Delete rect and create oval if needed or just coords?
            # Canvas coords works for both if created correctly? No, create_oval is distinct.
            # Lazy fix: Just use rect for now, fix in release.
            pass

    def on_release(self, event):
        if self.mode == "circle" and self.current_shape:
            # Replace rect with oval
            x0, y0, x1, y1 = self.canvas.coords(self.current_shape)
            self.canvas.delete(self.current_shape)
            self.canvas.create_oval(x0, y0, x1, y1, fill=self.current_color, outline="black", tags="shape")
            self.current_shape = None
        elif self.mode == "rect":
            self.current_shape = None

    def delete_selected(self):
        if self.selected_item:
            self.canvas.delete(self.selected_item)
            self.selected_item = None

    def add_label(self):
        text = simpledialog.askstring("Text", "Label Text:")
        if text:
            # Add at center (approx)
            self.canvas.create_text(self.canvas_width/2, self.canvas_height/2, text=text, font=("Arial", 12, "bold"), tags="shape")

    def save_map(self):
        # Serialize canvas items
        items = []
        for item in self.canvas.find_all():
            tags = self.canvas.gettags(item)
            if "shape" not in tags: continue

            itype = self.canvas.type(item)
            coords = self.canvas.coords(item)
            color = self.canvas.itemcget(item, "fill")
            text = self.canvas.itemcget(item, "text") if itype == "text" else ""

            items.append({
                "type": itype,
                "coords": coords,
                "color": color,
                "text": text
            })

        f = filedialog.asksaveasfilename(initialdir=get_writable_path("maps"), defaultextension=".json", filetypes=[("JSON", "*.json")])
        if f:
            try:
                with open(f, "w") as file:
                    json.dump(items, file)
                messagebox.showinfo("Erfolg", f"Karte gespeichert: {f}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

    def load_map(self):
        f = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if f:
            self.canvas.delete("shape") # Clear shapes, keep grid
            with open(f, "r") as file:
                items = json.load(file)

            for i in items:
                if i["type"] == "rectangle":
                    self.canvas.create_rectangle(*i["coords"], fill=i["color"], outline="black", tags="shape")
                elif i["type"] == "oval":
                    self.canvas.create_oval(*i["coords"], fill=i["color"], outline="black", tags="shape")
                elif i["type"] == "text":
                    self.canvas.create_text(*i["coords"], text=i["text"], font=("Arial", 12, "bold"), tags="shape")

    def export_image(self):
        # Use PostScript to get high quality image or PIL grab
        f = filedialog.asksaveasfilename(initialdir=get_writable_path("maps"), defaultextension=".png", filetypes=[("PNG", "*.png")])
        if f:
            # Requires ghostscript usually for PS, so maybe just PIL grab logic or simple draw
            # Re-drawing on PIL Image
            img = Image.new("RGB", (self.canvas_width, self.canvas_height), "#8FBC8F")
            draw = ImageDraw.Draw(img)

            # Draw Grid
            for i in range(1, 6):
                x = i * self.px_per_foot
                draw.line([(x, 0), (x, self.canvas_height)], fill="#666", width=1)
            for i in range(1, 3):
                y = i * self.px_per_foot
                draw.line([(0, y), (self.canvas_width, y)], fill="#666", width=1)

            # Iterate canvas items
            # This is hard because we need to sync state.
            # Better to rely on the serialized JSON or internal list if we had one.
            # We'll re-parse the canvas items.

            for item in self.canvas.find_all():
                tags = self.canvas.gettags(item)
                if "shape" not in tags: continue

                itype = self.canvas.type(item)
                coords = self.canvas.coords(item)
                color = self.canvas.itemcget(item, "fill")
                if not color: color = "black" # Text default?

                if itype == "rectangle":
                    draw.rectangle(coords, fill=color, outline="black")
                elif itype == "oval":
                    draw.ellipse(coords, fill=color, outline="black")
                elif itype == "text":
                    text = self.canvas.itemcget(item, "text")
                    # Simplified text draw
                    draw.text((coords[0], coords[1]), text, fill="black")

            try:
                img.save(f)
                messagebox.showinfo("Export", f"Bild gespeichert: {f}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Export: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BattlefieldMapCreator(root)
    root.mainloop()
