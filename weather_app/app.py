import streamlit as st
import requests

API_KEY = "your_api_key_here"

st.title("🌦️ WeatherX Dashboard")

city = st.text_input("Enter City")

if st.button("Get Weather"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()

    if data.get("main"):
        st.write("Temperature:", data["main"]["temp"], "°C")
        st.write("Humidity:", data["main"]["humidity"], "%")
    else:
        st.error("City not found")
