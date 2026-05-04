import os
from PIL import Image, ImageDraw
import customtkinter as ctk

def to_celsius(k):
    return k - 273.15

def to_fahrenheit(k):
    return (k - 273.15) * 9/5 + 32

def set_background(condition, left_panel):
    # Map condition to background image
    condition = condition.lower()
    if 'clear' in condition or 'sun' in condition:
        bg_path = 'assets/backgrounds/sunny.png'
    elif 'rain' in condition or 'drizzle' in condition:
        bg_path = 'assets/backgrounds/rainy.png'
    elif 'cloud' in condition:
        bg_path = 'assets/backgrounds/cloudy.png'
    elif 'snow' in condition:
        bg_path = 'assets/backgrounds/snowy.png'
    elif 'night' in condition:
        bg_path = 'assets/backgrounds/night.png'
    else:
        bg_path = 'assets/backgrounds/cloudy.png'

    if os.path.exists(bg_path):
        # Load and resize image
        img = Image.open(bg_path)
        img = img.resize((400, 650), Image.Resampling.LANCZOS)

        # Apply semi-transparent overlay
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 100))  # Semi-transparent black
        img = Image.alpha_composite(img.convert('RGBA'), overlay)

        # Convert to CTkImage
        bg_image = ctk.CTkImage(img, size=(400, 650))

        # Assuming left_panel has a background label
        # This will be set in main.py
        return bg_image
    else:
        return None