import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
import threading
import time
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

from api_handler import get_current_weather, get_forecast, get_aqi, get_city_timezone, get_hourly_forecast
from ui_components import InfoCard, ForecastCard, AQIBar
from utils import to_celsius, to_fahrenheit, set_background

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WeatherX — Live Weather Dashboard")
        self.geometry("1000x650")
        self.resizable(False, False)
        self.center_window()

        # Variables
        self.unit = "C"  # C or F
        self.current_data = None
        self.search_history = []
        self.clock_after_id = None
        self.timezone = None
        self.coord_mode = False  # False for city name, True for coordinates

        # Fonts
        self.city_font = ctk.CTkFont(size=32, weight="bold")
        self.temp_font = ctk.CTkFont(size=64, weight="bold")
        self.section_font = ctk.CTkFont(size=14, weight="bold")
        self.value_font = ctk.CTkFont(size=20)
        self.clock_font = ctk.CTkFont(size=13)

        # Colors
        self.bg_color = "#1a1a2e"
        self.card_color = "#16213e"
        self.accent_color = "#0f3460"

        self.configure(fg_color=self.bg_color)

        # Create panels
        self.left_panel = ctk.CTkFrame(self, width=400, height=650, fg_color=self.bg_color)
        self.left_panel.pack(side="left", fill="y")
        self.left_panel.pack_propagate(False)

        self.right_panel = ctk.CTkFrame(self, width=600, height=650, fg_color=self.bg_color)
        self.right_panel.pack(side="right", fill="both", expand=True)
        self.right_panel.pack_propagate(False)

        # Background label for left panel
        self.bg_label = ctk.CTkLabel(self.left_panel, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Left panel widgets
        self.search_frame = ctk.CTkFrame(self.left_panel, fg_color=self.card_color, corner_radius=15)
        self.search_frame.pack(pady=(20, 10), padx=20, fill="x")

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Enter city name or lat,lon", font=ctk.CTkFont(size=14))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(15, 5), pady=10)
        self.search_entry.bind("<Return>", lambda e: self.on_search())

        self.coord_button = ctk.CTkButton(self.search_frame, text="📍", width=40, command=self.toggle_coord_mode)
        self.coord_button.pack(side="right", padx=(0, 5), pady=10)

        self.search_button = ctk.CTkButton(self.search_frame, text="🔍", width=50, command=self.on_search)
        self.search_button.pack(side="right", padx=(5, 15), pady=10)

        self.history_menu = ctk.CTkOptionMenu(self.left_panel, values=["History"], command=self.on_history_select, fg_color=self.card_color)
        self.history_menu.pack(pady=(0, 20), padx=20, fill="x")

        self.city_label = ctk.CTkLabel(self.left_panel, text="City", font=self.city_font, text_color="#ffffff")
        self.city_label.pack(pady=(10, 0))

        self.country_label = ctk.CTkLabel(self.left_panel, text="Country", font=ctk.CTkFont(size=14), text_color="#888888")
        self.country_label.pack()

        self.temp_label = ctk.CTkLabel(self.left_panel, text="25°C", font=self.temp_font, text_color="#ffffff")
        self.temp_label.pack(pady=(20, 10))

        self.condition_icon_label = ctk.CTkLabel(self.left_panel, text="☀️", font=ctk.CTkFont(size=80))
        self.condition_icon_label.pack()

        self.condition_label = ctk.CTkLabel(self.left_panel, text="Clear Sky", font=ctk.CTkFont(size=18))
        self.condition_label.pack(pady=(10, 5))

        self.feels_like_label = ctk.CTkLabel(self.left_panel, text="Feels like 27°C", font=ctk.CTkFont(size=14))
        self.feels_like_label.pack(pady=(5, 10))

        self.sunrise_label = ctk.CTkLabel(self.left_panel, text="🌅 Sunrise: 06:00", font=ctk.CTkFont(size=14))
        self.sunrise_label.pack(pady=(5, 5))

        self.sunset_label = ctk.CTkLabel(self.left_panel, text="🌇 Sunset: 18:00", font=ctk.CTkFont(size=14))
        self.sunset_label.pack(pady=(5, 10))

        self.clock_label = ctk.CTkLabel(self.left_panel, text="Mon, 05 May 2025 | 14:32:08", font=self.clock_font, text_color="#888888")
        self.clock_label.pack(pady=(10, 10))

        self.unit_switch = ctk.CTkSwitch(self.left_panel, text="°C / °F", command=self.toggle_unit, onvalue="F", offvalue="C")
        self.unit_switch.pack(pady=(10, 20))

        self.refresh_button = ctk.CTkButton(self.left_panel, text="🔄", width=50, command=self.refresh_weather)
        self.refresh_button.pack(pady=(0, 20))

        # Right panel with tabs
        self.tabview = ctk.CTkTabview(self.right_panel, width=580, height=610)
        self.tabview.pack(pady=(20, 20), padx=10)

        self.tabview.add("Current")
        self.tabview.add("Forecast")
        self.tabview.add("Hourly")
        self.tabview.add("Charts")
        self.tabview.add("Analysis")

        # Current tab
        self.current_tab = self.tabview.tab("Current")
        self.current_tab.configure(fg_color=self.bg_color)

        # Info cards
        self.info_frame = ctk.CTkFrame(self.current_tab, fg_color=self.bg_color)
        self.info_frame.pack(pady=(10, 10), padx=10, fill="x")

        self.humidity_card = InfoCard(self.info_frame, "💧", "Humidity", "60%")
        self.humidity_card.grid(row=0, column=0, padx=10, pady=10)

        self.wind_card = InfoCard(self.info_frame, "💨", "Wind Speed", "10 km/h")
        self.wind_card.grid(row=0, column=1, padx=10, pady=10)

        self.pressure_card = InfoCard(self.info_frame, "🔵", "Pressure", "1013 hPa")
        self.pressure_card.grid(row=1, column=0, padx=10, pady=10)

        self.visibility_card = InfoCard(self.info_frame, "👁️", "Visibility", "10 km")
        self.visibility_card.grid(row=1, column=1, padx=10, pady=10)

        # AQI
        self.aqi_bar = AQIBar(self.current_tab)
        self.aqi_bar.pack(pady=(10, 10), padx=10, fill="x")

        # Forecast tab
        self.forecast_tab = self.tabview.tab("Forecast")
        self.forecast_tab.configure(fg_color=self.bg_color)

        self.forecast_label = ctk.CTkLabel(self.forecast_tab, text="7-Day Forecast", font=self.section_font)
        self.forecast_label.pack(pady=(10, 10))

        self.forecast_cards = []
        forecast_container = ctk.CTkFrame(self.forecast_tab, fg_color=self.bg_color)
        forecast_container.pack(fill="x", padx=10)

        for i in range(7):
            card = ForecastCard(forecast_container, "Mon", "☀️", "25", "20")
            card.pack(side="left", padx=5)
            self.forecast_cards.append(card)

        # Hourly tab
        self.hourly_tab = self.tabview.tab("Hourly")
        self.hourly_tab.configure(fg_color=self.bg_color)

        self.hourly_label = ctk.CTkLabel(self.hourly_tab, text="24-Hour Forecast", font=self.section_font)
        self.hourly_label.pack(pady=(10, 10))

        self.hourly_frame = ctk.CTkScrollableFrame(self.hourly_tab, fg_color=self.bg_color, height=400)
        self.hourly_frame.pack(fill="both", padx=10, pady=10)

        # Charts tab
        self.charts_tab = self.tabview.tab("Charts")
        self.charts_tab.configure(fg_color=self.bg_color)

        # Analysis tab
        self.analysis_tab = self.tabview.tab("Analysis")
        self.analysis_tab.configure(fg_color=self.bg_color)

        self.analysis_text = ctk.CTkTextbox(self.analysis_tab, wrap="word")
        self.analysis_text.pack(fill="both", padx=10, pady=10, expand=True)

        # Loading label
        self.loading_label = ctk.CTkLabel(self.left_panel, text="", font=ctk.CTkFont(size=16))
        self.loading_label.pack(pady=(10, 10))

        # Auto load default city
        self.after(100, lambda: self.load_weather("London"))

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def toggle_unit(self):
        self.unit = self.unit_switch.get()
        if self.current_data:
            self.update_ui(self.current_data)

    def on_search(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a city name or coordinates.")
            return
        self.load_weather(query)

    def toggle_coord_mode(self):
        self.coord_mode = not self.coord_mode
        if self.coord_mode:
            self.search_entry.configure(placeholder_text="Enter coordinates (lat,lon)")
            self.coord_button.configure(fg_color="#4CAF50")  # Green when active
        else:
            self.search_entry.configure(placeholder_text="Enter city name")
            self.coord_button.configure(fg_color=["#3B8ED0", "#1F6AA5"])  # Default color

    def on_history_select(self, location):
        if location != "History":
            self.load_weather(location)

    def refresh_weather(self):
        if self.current_data:
            location = self.current_data['location']
            self.load_weather(location)

    def load_weather(self, location):
        self.loading_label.configure(text="Loading...")
        self.search_button.configure(state="disabled")
        threading.Thread(target=self.fetch_weather, args=(location,), daemon=True).start()

    def fetch_weather(self, location):
        try:
            current = get_current_weather(location)
            forecast = get_forecast(current['lat'], current['lon'])
            hourly = get_hourly_forecast(current['lat'], current['lon'])
            aqi, aqi_label = get_aqi(current['lat'], current['lon'])
            tz, current_time = get_city_timezone(current['lat'], current['lon'])
            data = {
                'current': current,
                'forecast': forecast,
                'hourly': hourly,
                'aqi': aqi,
                'aqi_label': aqi_label,
                'timezone': tz,
                'current_time': current_time,
                'location': location
            }
            self.after(0, lambda: self.update_ui(data))
        except Exception as e:
            message = str(e) if str(e) else "An unexpected error occurred."
            self.after(0, lambda: self.show_error(message))

    def show_error(self, msg):
        self.loading_label.configure(text="")
        self.search_button.configure(state="normal")
        if not msg:
            msg = "An unexpected error occurred."
        messagebox.showerror("Error", msg)

    def update_ui(self, data):
        self.current_data = data
        current = data['current']
        forecast = data['forecast']
        hourly = data.get('hourly', [])
        aqi = data['aqi']
        tz = data['timezone']

        # Update search history
        if data['location'] not in self.search_history:
            self.search_history.append(data['location'])
            if len(self.search_history) > 5:
                self.search_history.pop(0)
        self.history_menu.configure(values=self.search_history or ["History"])

        # Left panel
        self.city_label.configure(text=current['city'])
        self.country_label.configure(text=current['country'])
        temp = to_celsius(current['temp']) if self.unit == "C" else to_fahrenheit(current['temp'])
        color = "#ff6b6b" if temp > 30 else "#74b9ff" if temp < 10 else "#ffffff"
        self.temp_label.configure(text=f"{temp:.1f}°{self.unit}", text_color=color)

        # Icon (use emoji based on condition)
        icon_map = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Drizzle': '🌦️',
            'Thunderstorm': '⛈️',
            'Snow': '❄️',
            'Mist': '🌫️'
        }
        icon = icon_map.get(current['condition'], '☀️')
        self.condition_icon_label.configure(text=icon)

        self.condition_label.configure(text=current['condition_description'].capitalize())

        feels_like = to_celsius(current['feels_like']) if self.unit == "C" else to_fahrenheit(current['feels_like'])
        self.feels_like_label.configure(text=f"Feels like {feels_like:.1f}°{self.unit}")

        sunrise = datetime.fromtimestamp(current['sunrise']).strftime('%H:%M')
        sunset = datetime.fromtimestamp(current['sunset']).strftime('%H:%M')
        self.sunrise_label.configure(text=f"🌅 Sunrise: {sunrise}")
        self.sunset_label.configure(text=f"🌇 Sunset: {sunset}")

        # Background
        bg_img = set_background(current['condition'], self.left_panel)
        if bg_img:
            self.bg_label.configure(image=bg_img)
            self.bg_label.image = bg_img  # Keep reference

        # Start clock
        self.start_clock(tz)

        # Current tab
        self.humidity_card.update_value(f"{current['humidity']}%")
        wind_kmh = current['wind_speed'] * 3.6  # m/s to km/h
        self.wind_card.update_value(f"{wind_kmh:.1f} km/h")
        self.pressure_card.update_value(f"{current['pressure']} hPa")
        self.visibility_card.update_value(f"{current['visibility']:.1f} km")

        self.aqi_bar.update_aqi(aqi)

        # Forecast tab
        for i, day in enumerate(forecast[:7]):  # Limit to 7 days
            date_obj = datetime.strptime(day['date'], '%Y-%m-%d')
            day_name = date_obj.strftime('%a')
            icon = icon_map.get(day['condition'], '☀️')
            high = to_celsius(day['avg_temp']) if self.unit == "C" else to_fahrenheit(day['avg_temp'])
            low = high - 5  # Placeholder, API gives avg, not high/low
            self.forecast_cards[i].update(day_name, icon, f"{high:.0f}", f"{low:.0f}")

        # Hourly tab
        # Clear previous hourly cards
        for widget in self.hourly_frame.winfo_children():
            widget.destroy()

        for item in hourly[:24]:  # Limit to 24 hours
            time_str = item['time'].strftime('%H:%M')
            temp = to_celsius(item['temp']) if self.unit == "C" else to_fahrenheit(item['temp'])
            icon = icon_map.get(item['condition'], '☀️')
            card = ctk.CTkFrame(self.hourly_frame, fg_color=self.card_color, corner_radius=10)
            card.pack(fill="x", padx=5, pady=5)
            
            time_label = ctk.CTkLabel(card, text=time_str, font=ctk.CTkFont(size=12, weight="bold"))
            time_label.pack(pady=(5, 2))
            
            icon_label = ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=24))
            icon_label.pack()
            
            temp_label = ctk.CTkLabel(card, text=f"{temp:.1f}°", font=ctk.CTkFont(size=14))
            temp_label.pack(pady=(2, 5))

        # Charts tab
        self.update_charts(data)

        # Analysis tab
        self.update_analysis(data)

        self.loading_label.configure(text="")
        self.search_button.configure(state="normal")

    def update_charts(self, data):
        # Clear previous charts
        for widget in self.charts_tab.winfo_children():
            widget.destroy()

        forecast = data['forecast']
        hourly = data.get('hourly', [])

        if not forecast and not hourly:
            return

        # Temperature chart
        fig, ax = plt.subplots(figsize=(5, 3), facecolor='#1a1a2e')
        ax.set_facecolor('#1a1a2e')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')

        if hourly:
            times = [item['time'] for item in hourly[:24]]
            temps = [to_celsius(item['temp']) if self.unit == "C" else to_fahrenheit(item['temp']) for item in hourly[:24]]
            ax.plot(times, temps, color='#74b9ff', linewidth=2)
            ax.set_title('24-Hour Temperature Trend', color='white')
            ax.set_ylabel(f'Temperature (°{self.unit})', color='white')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            plt.setp(ax.get_xticklabels(), rotation=45)

        canvas = FigureCanvasTkAgg(fig, master=self.charts_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_analysis(self, data):
        current = data['current']
        forecast = data['forecast']
        analysis = f"Weather Analysis for {current['city']}, {current['country']}\n\n"
        analysis += f"Current Conditions:\n"
        analysis += f"- Temperature: {to_celsius(current['temp']):.1f}°C / {to_fahrenheit(current['temp']):.1f}°F\n"
        analysis += f"- Condition: {current['condition_description'].capitalize()}\n"
        analysis += f"- Humidity: {current['humidity']}%\n"
        analysis += f"- Wind Speed: {current['wind_speed'] * 3.6:.1f} km/h\n"
        analysis += f"- Air Quality: {data['aqi_label']} (AQI: {data['aqi']})\n\n"

        if forecast:
            analysis += f"7-Day Forecast Summary:\n"
            for i, day in enumerate(forecast[:7]):
                date_obj = datetime.strptime(day['date'], '%Y-%m-%d')
                temp = to_celsius(day['avg_temp']) if self.unit == "C" else to_fahrenheit(day['avg_temp'])
                analysis += f"- {date_obj.strftime('%A')}: {temp:.1f}°{self.unit}, {day['condition']}\n"

            # Simple analysis
            temps = [to_celsius(day['avg_temp']) for day in forecast[:7]]
            avg_temp = sum(temps) / len(temps)
            analysis += f"\nWeekly Average Temperature: {avg_temp:.1f}°C\n"
            if avg_temp > 25:
                analysis += "It's going to be warm this week!\n"
            elif avg_temp < 10:
                analysis += "Expect cooler weather this week.\n"
            else:
                analysis += "Moderate temperatures expected.\n"

        self.analysis_text.delete("0.0", "end")
        self.analysis_text.insert("0.0", analysis)

    def start_clock(self, tz):
        if self.clock_after_id:
            self.after_cancel(self.clock_after_id)
        self.timezone = tz
        self.update_clock()

    def update_clock(self):
        if self.timezone:
            now = datetime.now(self.timezone)
            time_str = now.strftime('%a, %d %b %Y | %H:%M:%S')
            self.clock_label.configure(text=time_str)
        self.clock_after_id = self.after(1000, self.update_clock)

if __name__ == "__main__":
    app = App()
    app.mainloop()