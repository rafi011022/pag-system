# kafka/producer.py
from kafka import KafkaProducer
import json
import random
import time
from datetime import datetime

bootstrap_servers = ['localhost:9092', 'localhost:9093', 'localhost:9094']
producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',
    retries=3
)

regions = ["Sylhet", "Dhaka", "Chittagong", "Kurigram", "Sunamganj", "Barisal", "Khulna"]
disaster_types = ["Flood", "Cyclone", "Drought", "Landslide"]

print("🚀 Kafka Producer Running... (Press Ctrl+C to stop)")

while True:
    data = {
        "rainfall_mm": random.choice([10, 50, 100, 200, 500, 1000]),
        "wind_speed_kmh": random.choice([10, 20, 50, 100, 150, 300]),
        "river_level_m": round(random.uniform(1, 20), 2),
        "temperature_c": round(random.uniform(20, 50), 2),
        "humidity": round(random.uniform(30, 100), 2),
        "region": random.choice(regions),
        "disaster_type": random.choice(disaster_types),
        "timestamp": datetime.now().isoformat()
    }
    producer.send('bmd_data', data)
    print(f"📤 Sent to Kafka: {data}")
    time.sleep(2)
