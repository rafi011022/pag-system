# data/fetch_bmd_data.py
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

BMD_API_URLS = {
    "rainfall": "https://api.bmd.gov.bd/weather/rainfall",
    "temperature": "https://api.bmd.gov.bd/weather/temperature",
    "wind": "https://api.bmd.gov.bd/weather/wind",
    "humidity": "https://api.bmd.gov.bd/weather/humidity"
}

def fetch_bmd_data():
    try:
        response = requests.get(BMD_API_URLS["rainfall"], timeout=10)
        if response.status_code == 200:
            data = response.json()
            for station in data:
                kafka_data = {
                    "source": "BMD",
                    "data_type": "rainfall",
                    "station_id": station.get("station_id", "N/A"),
                    "station_name": station.get("station_name", "N/A"),
                    "region": station.get("region", "N/A"),
                    "rainfall_mm": station.get("rainfall_mm", 0),
                    "timestamp": datetime.now().isoformat(),
                    "unit": "mm"
                }
                producer.send('bmd_data', kafka_data)
                print(f"📤 Sent BMD Rainfall Data: {station.get('region')}")

        response = requests.get(BMD_API_URLS["temperature"], timeout=10)
        if response.status_code == 200:
            data = response.json()
            for station in data:
                kafka_data = {
                    "source": "BMD",
                    "data_type": "temperature",
                    "station_id": station.get("station_id", "N/A"),
                    "station_name": station.get("station_name", "N/A"),
                    "region": station.get("region", "N/A"),
                    "temperature_c": station.get("temperature_c", 0),
                    "timestamp": datetime.now().isoformat(),
                    "unit": "°C"
                }
                producer.send('bmd_data', kafka_data)
                print(f"📤 Sent BMD Temperature Data: {station.get('region')}")

    except Exception as e:
        print(f"❌ Error fetching BMD data: {e}")

print("🌦️ BMD Data Fetcher Running... (Press Ctrl+C to stop)")
while True:
    fetch_bmd_data()
    time.sleep(3600)
