from PIL import Image, ImageDraw, ImageFont
import os

def create_sw_legion_icon():
    # Create a 256x256 icon image
    size = (256, 256)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background circle (dark blue/black)
    circle_color = (25, 25, 50, 255)  # Dark blue
    draw.ellipse([20, 20, 236, 236], fill=circle_color, outline=(100, 100, 150, 255), width=4)
    
    # Inner circle (lighter blue)
    inner_color = (50, 70, 120, 255)  # Lighter blue
    draw.ellipse([40, 40, 216, 216], fill=inner_color, outline=(150, 150, 200, 255), width=2)
    
    # Central emblem - simplified Imperial symbol style
    center_x, center_y = 128, 128
    
    # Draw hexagon shape (simplified)
    points = []
    import math
    for i in range(6):
        angle = i * math.pi / 3
        x = center_x + 60 * math.cos(angle)
        y = center_y + 60 * math.sin(angle)
        points.append((x, y))
    
    draw.polygon(points, fill=(200, 200, 200, 255), outline=(255, 255, 255, 255), width=3)
    
    # Central smaller circle
    draw.ellipse([108, 108, 148, 148], fill=(255, 255, 255, 255), outline=(200, 200, 200, 255), width=2)
    
    # Add some detail lines
    draw.line([128, 88, 128, 168], fill=(100, 100, 150, 255), width=3)
    draw.line([88, 128, 168, 128], fill=(100, 100, 150, 255), width=3)
    
    # Save as ICO file
    ico_path = "sw_legion_logo.ico"
    
    # Create multiple sizes for the ICO file
    sizes = [256, 128, 64, 48, 32, 16]
    images = []
    
    for size in sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        images.append(resized)
    
    # Save as ICO with multiple sizes
    img.save(ico_path, format='ICO', sizes=[(s, s) for s in sizes])
    print(f"Icon created: {ico_path}")

if __name__ == "__main__":
    create_sw_legion_icon()