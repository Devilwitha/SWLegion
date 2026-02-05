from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
import json
import logging

class MapRenderer:
    @staticmethod
    def draw_map(deployment_name, w=800, h=400, db=None):
        """Generates a PIL Image of the map based on deployment name."""
        img = Image.new("RGB", (w, h), "#e1f5fe")
        draw = ImageDraw.Draw(img)
        
        # Load Fonts
        try:
            font = ImageFont.truetype("arial.ttf", 20)
            font_s = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
            font_s = ImageFont.load_default()

        # Helper
        def ft_to_px_w(ft): return (ft / 6.0) * w
        def ft_to_px_h(ft): return (ft / 3.0) * h

        # Draw Border
        draw.rectangle([0, 0, w-1, h-1], outline="#0288d1", width=2)

        # 1. Custom Maps (from DB or JSON)
        custom_card = None
        if db:
            custom_card = next((c for c in db.battle_cards if c["name"] == deployment_name and c.get("category") == "Deployment"), None)

        used_custom = False
        if custom_card and custom_card.get("map_file") and os.path.exists(custom_card["map_file"]):
            try:
                with open(custom_card["map_file"], "r") as f:
                    zones = json.load(f)

                scale_x = w / 600.0  # Original creator Size
                scale_y = h / 300.0

                for z in zones:
                    c = z["color"]
                    coords = z["coords"]
                    x0 = coords[0] * scale_x
                    y0 = coords[1] * scale_y
                    x1 = coords[2] * scale_x
                    y1 = coords[3] * scale_y

                    fill = "#ffcdd2" if c == "red" else "#bbdefb"
                    outline = "red" if c == "red" else "blue"
                    draw.rectangle([x0, y0, x1, y1], fill=fill, outline=outline)
                used_custom = True
            except Exception as e:
                logging.error(f"MapRenderer: Failed to load custom map file: {e}")

        # 2. Standard Maps
        if not used_custom:
            mode = deployment_name
            
            if mode == "Battle Lines":
                range_1_px = ft_to_px_h(0.5)
                draw.rectangle([0, 0, w, range_1_px], fill="#ffcdd2", outline="red")
                draw.text((w/2, range_1_px/2), "ROT ZONE", fill="black", font=font, anchor="mm")
                draw.rectangle([0, h-range_1_px, w, h], fill="#bbdefb", outline="blue")
                draw.text((w/2, h-(range_1_px/2)), "BLAU ZONE", fill="black", font=font, anchor="mm")

            elif mode == "The Long March":
                range_1_px = ft_to_px_w(0.5)
                draw.rectangle([0, 0, range_1_px, h], fill="#bbdefb", outline="blue")
                draw.text((range_1_px/2, h/2), "BLAU", fill="black", font=font, anchor="mm")
                draw.rectangle([w-range_1_px, 0, w, h], fill="#ffcdd2", outline="red")
                draw.text((w-(range_1_px/2), h/2), "ROT", fill="black", font=font, anchor="mm")

            elif mode == "Major Offensive":
                corner_w = ft_to_px_w(2.0)
                corner_h = ft_to_px_h(1.0)
                draw.rectangle([0, h-corner_h, corner_w, h], fill="#bbdefb", outline="blue")
                draw.text((corner_w/3, h-corner_h/2), "BLAU", fill="black", font=font, anchor="mm")
                draw.rectangle([w-corner_w, 0, w, corner_h], fill="#ffcdd2", outline="red")
                draw.text((w-corner_w/3, corner_h/2), "ROT", fill="black", font=font, anchor="mm")
            
            elif mode == "Disarray":
                corner_w = ft_to_px_w(1.5)
                corner_h = ft_to_px_h(1.0)
                draw.rectangle([0, 0, corner_w, corner_h], fill="#bbdefb", outline="blue")
                draw.rectangle([w-corner_w, h-corner_h, w, h], fill="#bbdefb", outline="blue")
                draw.rectangle([w-corner_w, 0, w, corner_h], fill="#ffcdd2", outline="red")
                draw.rectangle([0, h-corner_h, corner_w, h], fill="#ffcdd2", outline="red")

            elif mode == "Danger Close":
                range_2_px = ft_to_px_h(1.0) # Range 2 = 12 inch = 1ft
                draw.rectangle([0, 0, w, range_2_px], fill="#ffcdd2", outline="red")
                draw.text((w/2, range_2_px/2), "ROT (Rng 2)", fill="black", font=font, anchor="mm")
                draw.rectangle([0, h-range_2_px, w, h], fill="#bbdefb", outline="blue")
                draw.text((w/2, h-(range_2_px/2)), "BLAU (Rng 2)", fill="black", font=font, anchor="mm")

            elif mode == "Hemmed In":
                cx, cy = w/2, h/2
                r = ft_to_px_h(0.75)
                # Draw Blue Circle
                draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill="#bbdefb", outline="blue")
                draw.text((cx, cy), "BLAU", fill="black", font=font, anchor="mm")
                
                # Draw Red Strips
                strip = ft_to_px_w(0.5)
                draw.rectangle([0, 0, strip, h], fill="#ffcdd2", outline="red")
                draw.rectangle([w-strip, 0, w, h], fill="#ffcdd2", outline="red")

            elif "Hinterhalt" in mode or "Ambush" in mode:
                strip = ft_to_px_w(0.5)
                draw.rectangle([0, 0, w, h], fill="#e1f5fe", outline=None)
                # Red perimeter
                draw.rectangle([0, 0, w, strip], fill="#ffcdd2")
                draw.rectangle([0, h-strip, w, h], fill="#ffcdd2")
                draw.rectangle([0, 0, strip, h], fill="#ffcdd2")
                draw.rectangle([w-strip, 0, w, h], fill="#ffcdd2")
                # Blue center
                box_w, box_h = ft_to_px_w(2), ft_to_px_h(1)
                cx, cy = w/2, h/2
                draw.rectangle([cx-box_w/2, cy-box_h/2, cx+box_w/2, cy+box_h/2], fill="#bbdefb", outline="blue")
                draw.text((cx, cy), "BLAU", fill="black", font=font, anchor="mm")

            else:
                 draw.text((w/2, h/2), f"Layout: {mode}", fill="black", font=font, anchor="mm")

        return img

    @staticmethod
    def draw_overlays(img, mission_name, blue_fac="", red_fac=""):
        """Adds text overlays and objective tokens to an existing map image."""
        w, h = img.size
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
            font_b = ImageFont.truetype("arialbd.ttf", 22)
            font_tok = ImageFont.truetype("arialbd.ttf", 16)
        except:
            font = ImageFont.load_default()
            font_b = ImageFont.load_default()
            font_tok = ImageFont.load_default()

        # Labels
        if blue_fac:
            draw.text((w/2, h-25), f"BLAU: {blue_fac}", fill="#0d47a1", font=font_b, anchor="mm")
        if red_fac:
            draw.text((w/2, 25), f"ROT: {red_fac}", fill="#b71c1c", font=font_b, anchor="mm")

        # Objectives
        def draw_token(x, y, label="?"):
            r = 14
            draw.ellipse([x-r, y-r, x+r, y+r], fill="#66bb6a", outline="green", width=2)
            # Text centering slightly adjusted for visual balance
            draw.text((x, y), label, fill="black", font=font_tok, anchor="mm")

        m_up = mission_name.upper()

        if "ABFANGEN" in m_up or "INTERCEPT" in m_up or "SCHLÜSSEL" in m_up or "KEY" in m_up:
            draw_token(w/2, h/2, "C")
            draw_token(w/4, h/2, "L")
            draw_token(3*w/4, h/2, "R")

        elif "DURCHBRUCH" in m_up or "BREAKTHROUGH" in m_up:
             draw.line([w/2, h-60, w/2, 60], fill="orange", width=6)
             draw.polygon([w/2, 50, w/2-15, 80, w/2+15, 80], fill="orange")
             draw.text((w/2 + 25, h/2), "ZIEL", fill="orange", font=font_b, anchor="lm")

        elif "ELIMINIERUNG" in m_up or "DEATHMATCH" in m_up:
            draw.text((w/2, h/2), "☠ KILL ☠", fill="red", font=font_b, anchor="mm")

        elif "EVAKUIERUNG" in m_up or "HOSTAGE" in m_up:
            draw_token(w/2, 50, "H(R)")
            draw_token(w/2, h-50, "H(B)")

        return img
