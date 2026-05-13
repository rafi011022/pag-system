# kafka/consumer.py
from kafka import KafkaConsumer, KafkaProducer
import json
import joblib
from datetime import datetime

clf = joblib.load("data/isolation_forest_bangladesh.pkl")

bootstrap_servers = ['localhost:9092', 'localhost:9093', 'localhost:9094']
consumer = KafkaConsumer(
    'bmd_data',
    bootstrap_servers=bootstrap_servers,
    group_id='pag-consumer-group',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    enable_auto_commit=True,
    auto_commit_interval_ms=5000
)

cleaned_producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all'
)

print("🔍 Kafka Consumer Running... (Press Ctrl+C to stop)")

for message in consumer:
    data = message.value
    print(f"\n📥 Received from Kafka: {data}")

    features = [[
        data.get("rainfall_mm", 0),
        data.get("wind_speed_kmh", 0),
        data.get("river_level_m", 0),
        data.get("temperature_c", 0)
    ]]

    if clf.predict(features)[0] == 1:
        data["cleaned_at"] = str(datetime.now())
        cleaned_producer.send('cleaned_bmd_data', data)
        print(f"✅ Cleaned data sent to 'cleaned_bmd_data': {data['region']}")
    else:
        print(f"❌ Anomaly detected (rejected): {data['region']} - {data}")
