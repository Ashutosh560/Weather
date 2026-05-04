import os
import requests
from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime

API_KEY = "0d6224cdd6d92b2a2942d8bac1e0acec" # Replace with your actual API key
BASE_URL = "https://api.openweathermap.org/data/2.5/"
AQI_URL = "http://api.openweathermap.org/data/2.5/air_pollution"

def get_current_weather(location):
    if ',' in location:  # Coordinates
        try:
            lat, lon = location.split(',')
            lat, lon = float(lat.strip()), float(lon.strip())
            url = f"{BASE_URL}weather?lat={lat}&lon={lon}&appid={API_KEY}"
            city_name = f"Lat: {lat:.2f}, Lon: {lon:.2f}"
        except ValueError:
            raise Exception("Invalid coordinates format. Use lat,lon")
    else:  # City name
        url = f"{BASE_URL}weather?q={location}&appid={API_KEY}"
        city_name = location

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        main = data['main']
        wind = data['wind']
        sys = data['sys']
        weather = data['weather'][0]
        return {
            'city': city_name.title() if ',' not in location else city_name,
            'temp': main['temp'],
            'feels_like': main['feels_like'],
            'min': main['temp_min'],
            'max': main['temp_max'],
            'humidity': main['humidity'],
            'wind_speed': wind['speed'],
            'pressure': main['pressure'],
            'visibility': data.get('visibility', 10000) / 1000,  # in km
            'condition': weather['main'],
            'condition_description': weather['description'],
            'icon_code': weather['icon'],
            'sunrise': sys['sunrise'],
            'sunset': sys['sunset'],
            'country': sys.get('country', 'Unknown'),
            'lat': data['coord']['lat'],
            'lon': data['coord']['lon']
        }
    else:
        try:
            data = response.json()
            message = data.get('message', 'Unknown weather API error')
        except ValueError:
            message = response.text or 'Unknown weather API error'
        raise Exception(f"Weather API error: {message}")

def get_forecast(lat, lon):
    url = f"{BASE_URL}forecast?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        forecast = []
        # Get up to 7 days (56 items would be 7*8, but API gives 40)
        for i in range(0, min(56, len(data.get('list', []))), 8):
            day = data['list'][i]
            date = datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d')
            avg_temp = day['main']['temp']
            condition = day['weather'][0]['main']
            icon_code = day['weather'][0]['icon']
            forecast.append({
                'date': date,
                'avg_temp': avg_temp,
                'condition': condition,
                'icon_code': icon_code
            })
        if not forecast:
            raise Exception('Forecast data is incomplete')
        return forecast
    else:
        try:
            data = response.json()
            message = data.get('message', 'Unknown forecast API error')
        except ValueError:
            message = response.text or 'Unknown forecast API error'
        raise Exception(f"Forecast API error: {message}")

def get_aqi(lat, lon):
    url = f"{AQI_URL}?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        aqi = data['list'][0]['main']['aqi']
        labels = {1: 'Good', 2: 'Fair', 3: 'Moderate', 4: 'Poor', 5: 'Very Poor'}
        return aqi, labels[aqi]
    else:
        try:
            data = response.json()
            message = data.get('message', 'Unknown AQI API error')
        except ValueError:
            message = response.text or 'Unknown AQI API error'
        raise Exception(f"AQI API error: {message}")

def get_hourly_forecast(lat, lon):
    url = f"{BASE_URL}forecast?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        hourly = []
        for item in data.get('list', [])[:24]:  # Next 24 hours (8 items * 3h)
            dt = datetime.fromtimestamp(item['dt'])
            temp = item['main']['temp']
            condition = item['weather'][0]['main']
            hourly.append({
                'time': dt,
                'temp': temp,
                'condition': condition
            })
        return hourly
    else:
        return []

def get_city_timezone(lat, lon):
    tf = TimezoneFinder()
    tz_str = tf.timezone_at(lng=lon, lat=lat)
    if tz_str:
        tz = pytz.timezone(tz_str)
        now = datetime.now(tz)
        return tz, now.strftime('%a, %d %b %Y | %H:%M:%S')
    else:
        return None, "Timezone not found"