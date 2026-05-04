import customtkinter as ctk
from PIL import Image
import os

class InfoCard(ctk.CTkFrame):
    def __init__(self, master, icon, label, value, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#16213e", corner_radius=15)

        self.icon_label = ctk.CTkLabel(self, text=icon, font=ctk.CTkFont(size=24))
        self.icon_label.pack(pady=(15, 5))

        self.label = ctk.CTkLabel(self, text=label, font=ctk.CTkFont(size=12, weight="bold"))
        self.label.pack()

        self.value_label = ctk.CTkLabel(self, text=value, font=ctk.CTkFont(size=18))
        self.value_label.pack(pady=(5, 15))

    def update_value(self, value):
        self.value_label.configure(text=value)

class ForecastCard(ctk.CTkFrame):
    def __init__(self, master, day, icon, high, low, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#16213e", corner_radius=15)

        self.day_label = ctk.CTkLabel(self, text=day, font=ctk.CTkFont(size=12, weight="bold"))
        self.day_label.pack(pady=(10, 5))

        self.icon_label = ctk.CTkLabel(self, text=icon, font=ctk.CTkFont(size=32))
        self.icon_label.pack()

        self.temp_label = ctk.CTkLabel(self, text=f"{high}° / {low}°", font=ctk.CTkFont(size=14))
        self.temp_label.pack(pady=(5, 10))

    def update(self, day, icon, high, low):
        self.day_label.configure(text=day)
        self.icon_label.configure(text=icon)
        self.temp_label.configure(text=f"{high}° / {low}°")

class AQIBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#16213e", corner_radius=15)

        self.label = ctk.CTkLabel(self, text="Air Quality Index", font=ctk.CTkFont(size=14, weight="bold"))
        self.label.pack(pady=(15, 10))

        self.progress = ctk.CTkProgressBar(self, width=300, height=20)
        self.progress.pack(pady=(0, 10))
        self.progress.set(0)

        self.aqi_label = ctk.CTkLabel(self, text="Good", font=ctk.CTkFont(size=16))
        self.aqi_label.pack(pady=(0, 15))

    def update_aqi(self, aqi):
        if aqi:
            self.progress.set(aqi / 5.0)
            labels = {1: ('Good', '#00b894'), 2: ('Fair', '#fdcb6e'), 3: ('Moderate', '#e17055'), 4: ('Poor', '#d63031'), 5: ('Very Poor', '#6c5ce7')}
            label, color = labels.get(aqi, ('N/A', '#ffffff'))
            self.aqi_label.configure(text=label, text_color=color)
            self.progress.configure(progress_color=color)
        else:
            self.progress.set(0)
            self.aqi_label.configure(text="N/A")