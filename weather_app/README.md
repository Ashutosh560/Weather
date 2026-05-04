# WeatherX — Live Weather Dashboard

A modern, dark-themed weather application built with CustomTkinter and OpenWeatherMap API.

## Features

- Real-time weather data for any city or coordinates
- 7-day weather forecast (up to available data)
- 24-hour hourly forecast
- Air Quality Index (AQI)
- Live local time display
- Temperature unit toggle (°C / °F)
- Search history
- Interactive charts and temperature trends
- Weather analysis and insights
- Responsive UI with background images
- Error handling for network issues

## Setup

1. **Get OpenWeatherMap API Key**:
   - Sign up at [OpenWeatherMap](https://openweathermap.org/api)
   - Get your free API key
   - Replace `YOUR_OPENWEATHERMAP_API_KEY` in `api_handler.py`

2. **Install Dependencies**:
   ```bash
   pip install customtkinter requests Pillow geopy timezonefinder pytz matplotlib
   ```

3. **Add Background Images**:
   - Place the following images in `assets/backgrounds/`:
     - `sunny.png`
     - `rainy.png`
     - `cloudy.png`
     - `night.png`
     - `snowy.png`
   - Images should be at least 400x650 pixels
   - If images are not found, the app will run without backgrounds

4. **Run the App**:
   ```bash
   python main.py
   ```

## Usage

- **City Search**: Enter a city name in the search box and click search or press Enter.
- **Coordinate Search**: Click the 📍 button to toggle coordinate mode, then enter latitude,longitude (e.g., 40.7128,-74.0060).
- **Tabs**:
  - **Current**: Current weather conditions and metrics
  - **Forecast**: 7-day weather forecast
  - **Hourly**: 24-hour detailed forecast
  - **Charts**: Temperature trend charts
  - **Analysis**: Weather insights and analysis

## Project Structure

```
weather_app/
├── main.py                  # Main application with tabbed interface
├── api_handler.py           # API calls for weather data
├── ui_components.py         # UI components (cards, bars)
├── utils.py                 # Helper functions
├── README.md                # This file
└── assets/
    └── backgrounds/         # Background images
```
├── assets/
│   ├── backgrounds/         # Background images
│   └── icons/               # Weather icons (optional)
└── README.md
```

## Usage

- Enter a city name in the search bar and press Enter or click 🔍
- Use the °C / °F switch to toggle temperature units
- Click 🔄 to refresh current city's weather
- View 5-day forecast and AQI in the right panel
- Clock updates every second with local time

## Notes

- Default city on startup: London
- Search history saves last 5 cities
- Handles API errors gracefully
- Uses threading for non-blocking API calls