# data/fetch_bwdb_data.py
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

BWDB_API_URLS = {
    "river_levels": "https://api.bwdb.gov.bd/river-levels",
    "polder_conditions": "https://api.bwdb.gov.bd/polder-conditions"
}

def fetch_bwdb_data():
    try:
        response = requests.get(BWDB_API_URLS["river_levels"], timeout=10)
        if response.status_code == 200:
            data = response.json()
            for station in data:
                kafka_data = {
                    "source": "BWDB",
                    "data_type": "river_level",
                    "station_id": station.get("station_id", "N/A"),
                    "station_name": station.get("station_name", "N/A"),
                    "river_name": station.get("river_name", "N/A"),
                    "region": station.get("region", "N/A"),
                    "river_level_m": station.get("level_m", 0),
                    "danger_level_m": station.get("danger_level_m", 0),
                    "timestamp": datetime.now().isoformat(),
                    "unit": "m"
                }
                producer.send('bwdb_data', kafka_data)
                print(f"📤 Sent BWDB River Level Data: {station.get('river_name')}")

        response = requests.get(BWDB_API_URLS["polder_conditions"], timeout=10)
        if response.status_code == 200:
            data = response.json()
            for polder in data:
                kafka_data = {
                    "source": "BWDB",
                    "data_type": "polder_condition",
                    "polder_id": polder.get("polder_id", "N/A"),
                    "polder_name": polder.get("polder_name", "N/A"),
                    "region": polder.get("region", "N/A"),
                    "condition": polder.get("condition", 0),
                    "timestamp": datetime.now().isoformat()
                }
                producer.send('bwdb_data', kafka_data)
                print(f"📤 Sent BWDB Polder Data: {polder.get('polder_name')}")

    except Exception as e:
        print(f"❌ Error fetching BWDB data: {e}")

print("💧 BWDB Data Fetcher Running... (Press Ctrl+C to stop)")
while True:
    fetch_bwdb_data()
    time.sleep(21600)
