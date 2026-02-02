import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont

class CardPrinter:
    def __init__(self, root):
        self.root = root
        self.root.title("SW Legion: Card Printer (Layout Designer)")
        self.root.geometry("1000x700")

        self.custom_units_file = "db/custom_units.json"
        self.custom_cards_file = "db/custom_command_cards.json"
        self.custom_upgrades_file = "db/custom_upgrades.json"
        self.custom_battle_file = "db/custom_battle_cards.json"

        self.units_data = self.load_json(self.custom_units_file)
        self.cards_data = self.load_json(self.custom_cards_file)
        self.upgrades_data = self.load_json(self.custom_upgrades_file)
        self.battle_data = self.load_json(self.custom_battle_file)

        self.loaded_image = None
        self.preview_image = None # Helper for tkinter

        self.setup_ui()

    def load_json(self, filename):
        if not os.path.exists(filename): return []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []

    def setup_ui(self):
        # Top Bar: Selection
        top_frame = tk.Frame(self.root, pady=10, padx=10, bg="#ddd")
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text="1. Wähle Typ:", bg="#ddd").pack(side=tk.LEFT)
        self.cb_type = ttk.Combobox(top_frame, values=["Einheit", "Kommandokarte", "Ausrüstung", "Schlachtkarte"], state="readonly")
        self.cb_type.pack(side=tk.LEFT, padx=5)
        self.cb_type.bind("<<ComboboxSelected>>", self.update_obj_list)
        self.cb_type.current(0)

        tk.Label(top_frame, text="2. Wähle Objekt:", bg="#ddd").pack(side=tk.LEFT, padx=(20, 0))
        self.cb_obj = ttk.Combobox(top_frame, state="readonly", width=30)
        self.cb_obj.pack(side=tk.LEFT, padx=5)

        tk.Label(top_frame, text="3. Bild:", bg="#ddd").pack(side=tk.LEFT, padx=(20, 0))
        btn_upload = tk.Button(top_frame, text="Bild laden...", command=self.upload_image)
        btn_upload.pack(side=tk.LEFT, padx=5)

        btn_render = tk.Button(top_frame, text="Vorschau aktualisieren", command=self.render_card, bg="#2196F3", fg="white", font=("Segoe UI", 9, "bold"))
        btn_render.pack(side=tk.LEFT, padx=20)

        btn_save = tk.Button(top_frame, text="Als Bild speichern", command=self.save_image, bg="#4CAF50", fg="white", font=("Segoe UI", 9, "bold"))
        btn_save.pack(side=tk.LEFT, padx=5)

        # Main Area: Canvas
        self.canvas_frame = tk.Frame(self.root, bg="#333")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#333", width=750, height=525) # Standard aspect ratioish
        self.canvas.pack(anchor="center", pady=20)

        self.update_obj_list()

    def update_obj_list(self, event=None):
        mode = self.cb_type.get()
        values = []
        if mode == "Einheit":
            for u in self.units_data:
                name = u.get("unit_data", {}).get("name", "???")
                values.append(name)
        elif mode == "Ausrüstung":
             for u in self.upgrades_data:
                name = u.get("name", "???")
                values.append(name)
        elif mode == "Schlachtkarte":
            for b in self.battle_data:
                name = b.get("name", "???")
                values.append(name)
        else:
            for c in self.cards_data:
                name = c.get("name", "???")
                values.append(name)

        self.cb_obj["values"] = values
        if values: self.cb_obj.current(0)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Bilder", "*.png;*.jpg;*.jpeg")])
        if file_path:
            try:
                self.loaded_image = Image.open(file_path).convert("RGBA")
                messagebox.showinfo("Info", "Bild geladen. Klicke auf 'Vorschau aktualisieren'.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Bild konnte nicht geladen werden: {e}")

    def get_selected_data(self):
        mode = self.cb_type.get()
        name = self.cb_obj.get()

        if mode == "Einheit":
            for u in self.units_data:
                if u.get("unit_data", {}).get("name") == name:
                    return u.get("unit_data"), "unit"
        elif mode == "Ausrüstung":
            for u in self.upgrades_data:
                if u.get("name") == name:
                    return u, "upgrade"
        elif mode == "Schlachtkarte":
            for b in self.battle_data:
                if b.get("name") == name:
                    return b, "battle"
        else:
            for c in self.cards_data:
                if c.get("name") == name:
                    return c, "card"
        return None, None

    def render_card(self):
        data, mode = self.get_selected_data()
        if not data: return

        # Dimensions (Standard Poker Card @ 300dpi is approx 750x1050, Landscape 1050x750)
        # Unit Cards are horizontal usually. Command Cards vertical. Upgrades are Mini American (41x63mm) -> approx 480x740

        if mode == "unit":
            W, H = 1050, 750
        elif mode == "upgrade":
            W, H = 480, 740
        elif mode == "battle":
            W, H = 1050, 750 # Landscape
        else:
            W, H = 750, 1050

        base = Image.new("RGBA", (W, H), (255, 255, 255, 255))
        draw = ImageDraw.Draw(base)

        # 1. Background Image
        if self.loaded_image:
            # Resize logic (cover)
            img_ratio = self.loaded_image.width / self.loaded_image.height
            target_ratio = W / H

            if img_ratio > target_ratio:
                # Wider
                new_h = H
                new_w = int(H * img_ratio)
            else:
                new_w = W
                new_h = int(W / img_ratio)

            resized = self.loaded_image.resize((new_w, new_h), Image.LANCZOS)
            # Center crop
            left = (new_w - W) // 2
            top = (new_h - H) // 2
            base.paste(resized.crop((left, top, left + W, top + H)), (0, 0))

        # 2. Overlays (Semi-transparent panels)
        # Load Fonts (fallback to default if ttf not found)
        try:
            font_title = ImageFont.truetype("arial.ttf", 60)
            font_text = ImageFont.truetype("arial.ttf", 30)
            font_small = ImageFont.truetype("arial.ttf", 24)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
            font_small = ImageFont.load_default()

        if mode == "unit":
            # Header Bar
            draw.rectangle([20, 20, W-20, 100], fill=(0, 0, 0, 180))
            draw.text((40, 30), data.get("name", "Unknown"), font=font_title, fill="white")
            draw.text((W-150, 40), f"{data.get('points', 0)} Pkt", font=font_title, fill="#FFD700")

            # Left Panel (Stats)
            draw.rectangle([20, 120, 200, H-20], fill=(255, 255, 255, 200))
            y = 140
            draw.text((30, y), f"Rang: {data.get('rank')}", font=font_small, fill="black"); y+=40
            draw.text((30, y), f"HP: {data.get('hp')}", font=font_small, fill="black"); y+=40
            draw.text((30, y), f"Mut: {data.get('courage')}", font=font_small, fill="black"); y+=40
            draw.text((30, y), f"Speed: {data.get('speed')}", font=font_small, fill="black"); y+=40
            draw.text((30, y), f"Def: {data.get('defense')}", font=font_small, fill="black"); y+=40

            # Bottom Panel (Keywords & Weapons)
            draw.rectangle([220, H-300, W-20, H-20], fill=(0, 0, 0, 180))
            draw.text((240, H-280), "Keywords: " + data.get("info", ""), font=font_text, fill="white")

            wy = H-220
            for w in data.get("weapons", []):
                dice = w.get("dice", {})
                d_str = f"R:{dice.get('red')} B:{dice.get('black')} W:{dice.get('white')}"
                line = f"{w.get('name')} (Rng {w.get('range')[0]}-{w.get('range')[1]})  [{d_str}]"
                draw.text((240, wy), line, font=font_text, fill="white")
                wy += 35

        elif mode == "upgrade":
            # Vertical Small Card
            # Header
            draw.rectangle([10, 10, W-10, 80], fill=(0, 0, 0, 180))
            draw.text((20, 20), data.get("name", ""), font=font_text, fill="white")
            draw.text((W-100, 20), f"{data.get('points', 0)}", font=font_title, fill="#FFD700")

            # Type
            draw.text((20, 85), f"[{data.get('type', '')}]", font=font_small, fill="black", stroke_width=1, stroke_fill="white")

            # Bottom Text
            draw.rectangle([10, H-300, W-10, H-10], fill=(255, 255, 255, 220), outline="black", width=3)
            import textwrap
            lines = textwrap.wrap(data.get("text", ""), width=30)
            ty = H-280
            for line in lines:
                draw.text((20, ty), line, font=font_small, fill="black")
                ty += 30

        elif mode == "battle":
            # Header (Color coded by category)
            cat = data.get("category", "Objective")
            colors = {"Objective": "#b71c1c", "Deployment": "#0d47a1", "Condition": "#1b5e20"}
            col = colors.get(cat, "black")

            draw.rectangle([20, 20, W-20, 100], fill=col)
            draw.text((40, 30), cat.upper(), font=font_small, fill="white")
            draw.text((40, 60), data.get("name", ""), font=font_title, fill="white")

            # Main Text
            draw.rectangle([100, 200, W-100, H-100], fill=(255, 255, 255, 200), outline=col, width=5)

            import textwrap
            lines = textwrap.wrap(data.get("text", ""), width=50)
            ty = 250
            for line in lines:
                draw.text((120, ty), line, font=font_text, fill="black")
                ty += 40


        else: # Command Card
            # Header
            draw.rectangle([20, 20, W-20, 100], fill=(0, 0, 0, 180))
            pips = "•" * data.get("pips", 0)
            if data.get("pips") == 4: pips = "Standing"
            draw.text((40, 30), pips, font=font_title, fill="#FFD700")
            draw.text((40, 110), data.get("name", ""), font=font_title, fill="black", stroke_width=2, stroke_fill="white")

            # Bottom Text Box
            draw.rectangle([40, H-400, W-40, H-40], fill=(255, 255, 255, 220), outline="black", width=3)

            # Text Wrap (Simple)
            import textwrap
            lines = textwrap.wrap(data.get("text", ""), width=40)
            ty = H-380
            for line in lines:
                draw.text((60, ty), line, font=font_text, fill="black")
                ty += 35

        # Store and Display
        self.generated_image = base

        # Resize for preview
        preview_w = 700
        preview_h = int(preview_w * (H/W))
        if preview_h > 500:
            preview_h = 500
            preview_w = int(preview_h * (W/H))

        self.preview_image = ImageTk.PhotoImage(base.resize((preview_w, preview_h)))
        self.canvas.config(width=preview_w, height=preview_h)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.preview_image, anchor="nw")

    def save_image(self):
        if not hasattr(self, "generated_image"): return

        f = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if f:
            self.generated_image.save(f)
            messagebox.showinfo("Gespeichert", f"Bild gespeichert unter {f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CardPrinter(root)
    root.mainloop()
