# data/fetch_iot_data.py
import random
import json
from kafka import KafkaProducer
from datetime import datetime
import time

bootstrap_servers = ['localhost:9092', 'localhost:9093', 'localhost:9094']
producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

IOT_SENSORS = [
    {"sensor_id": "IOT-001", "region": "Sylhet", "lat": 24.89, "lon": 91.88, "type": "rainfall"},
    {"sensor_id": "IOT-002", "region": "Sylhet", "lat": 24.90, "lon": 91.89, "type": "soil_moisture"},
    {"sensor_id": "IOT-003", "region": "Kurigram", "lat": 25.81, "lon": 89.63, "type": "rainfall"},
    {"sensor_id": "IOT-004", "region": "Kurigram", "lat": 25.82, "lon": 89.64, "type": "water_level"},
    {"sensor_id": "IOT-005", "region": "Dhaka", "lat": 23.81, "lon": 90.41, "type": "temperature"},
    {"sensor_id": "IOT-006", "region": "Chittagong", "lat": 22.34, "lon": 91.81, "type": "humidity"}
]

def generate_iot_data():
    for sensor in IOT_SENSORS:
        if sensor["type"] == "rainfall":
            value, unit = round(random.uniform(0, 300), 2), "mm"
        elif sensor["type"] == "soil_moisture":
            value, unit = round(random.uniform(0, 100), 2), "%"
        elif sensor["type"] == "water_level":
            value, unit = round(random.uniform(0, 10), 2), "m"
        elif sensor["type"] == "temperature":
            value, unit = round(random.uniform(20, 50), 2), "°C"
        elif sensor["type"] == "humidity":
            value, unit = round(random.uniform(30, 100), 2), "%"
        else:
            value, unit = 0, ""

        data = {
            "source": "IoT",
            "sensor_id": sensor["sensor_id"],
            "region": sensor["region"],
            "lat": sensor["lat"],
            "lon": sensor["lon"],
            "data_type": sensor["type"],
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat()
        }
        producer.send('sensor_data', data)
        print(f"📡 Sent IoT Data: {sensor['sensor_id']} ({sensor['type']}) = {value} {unit}")

print("🌐 IoT Data Simulator Running... (Press Ctrl+C to stop)")
while True:
    generate_iot_data()
    time.sleep(300)
