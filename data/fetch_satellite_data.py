# data/fetch_satellite_data.py
import requests
import json
from kafka import KafkaProducer
from datetime import datetime
import time

bootstrap_servers = ['localhost:9092', 'localhost:9093', 'localhost:9094']
producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

API_KEY = "your_openweathermap_api_key"  # Replace with your API key
CITIES = ["Sylhet", "Dhaka", "Chittagong", "Kurigram", "Sunamganj", "Barisal", "Khulna"]

def fetch_satellite_data():
    for city in CITIES:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city},BD&appid={API_KEY}&units=metric"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                kafka_data = {
                    "source": "Satellite",
                    "city": city,
                    "rainfall_mm": data.get("rain", {}).get("1h", 0),
                    "cloud_cover": data.get("clouds", {}).get("all", 0),
                    "temperature_c": data.get("main", {}).get("temp", 0),
                    "humidity": data.get("main", {}).get("humidity", 0),
                    "wind_speed_kmh": data.get("wind", {}).get("speed", 0) * 3.6,
                    "timestamp": datetime.now().isoformat(),
                    "notes": "Placeholder for Sentinel/MODIS data"
                }
                producer.send('satellite_data', kafka_data)
                print(f"🛰️ Sent Satellite Data for {city}")
        except Exception as e:
            print(f"❌ Error fetching data for {city}: {e}")

print("🛰️ Satellite Data Fetcher Running... (Press Ctrl+C to stop)")
while True:
    fetch_satellite_data()
    time.sleep(86400)
