# database/db.py
import os
import psycopg2
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime

# ── PostgreSQL Config ─────────────────────────────────────────
PG_CONFIG = {
    "host":     os.getenv("PG_HOST", "localhost"),
    "port":     int(os.getenv("PG_PORT", 5432)),
    "database": os.getenv("PG_DATABASE", "pag_system"),
    "user":     os.getenv("PG_USER", "pag_user"),
    "password": os.getenv("PG_PASSWORD", "pag_password"),
}

# ── InfluxDB Config ───────────────────────────────────────────
INFLUX_URL    = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN  = os.getenv("INFLUX_TOKEN", "your-influxdb-token")
INFLUX_ORG    = os.getenv("INFLUX_ORG", "pag-org")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "pag-timeseries")

def get_db_connection():
    """Return a PostgreSQL connection."""
    return psycopg2.connect(**PG_CONFIG)

def get_influx_client():
    """Return an InfluxDB write client."""
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    return client, client.write_api(write_options=SYNCHRONOUS)

def write_sensor_to_influx(data: dict):
    """Write a sensor reading to InfluxDB."""
    client, write_api = get_influx_client()
    try:
        point = (
            Point("weather_sensor")
            .tag("region", data.get("region", "unknown"))
            .tag("source", data.get("source", "unknown"))
            .tag("disaster_type", data.get("disaster_type", "none"))
            .field("rainfall_mm",    float(data.get("rainfall_mm", 0)))
            .field("wind_speed_kmh", float(data.get("wind_speed_kmh", 0)))
            .field("river_level_m",  float(data.get("river_level_m", 0)))
            .field("temperature_c",  float(data.get("temperature_c", 0)))
            .field("humidity",       float(data.get("humidity", 0)))
            .time(datetime.utcnow())
        )
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        print(f"✅ InfluxDB: written for {data.get('region')}")
    except Exception as e:
        print(f"❌ InfluxDB write error: {e}")
    finally:
        client.close()

def write_risk_to_postgres(region, disaster_type, risk_score, risk_level, impact: dict):
    """Persist a risk assessment record to PostgreSQL."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO risk_assessments
               (region, disaster_type, risk_score, risk_level,
                estimated_affected, estimated_displaced,
                crop_damage_crore, economic_loss_crore, assessed_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW())""",
            (
                region, disaster_type, risk_score, risk_level,
                impact.get("estimated_affected", 0),
                impact.get("estimated_displaced", 0),
                impact.get("crop_damage_crore_bdt", 0),
                impact.get("economic_loss_crore_bdt", 0),
            )
        )
        conn.commit()
        print(f"✅ PostgreSQL: risk record saved for {region}")
    except Exception as e:
        conn.rollback()
        print(f"❌ PostgreSQL write error: {e}")
    finally:
        cur.close()
        conn.close()
