# 🌍 Predictive Anticipatory Governance (PAG) System for Bangladesh

A fully automated, real-time, multi-model system for disaster prediction, risk assessment, and policy generation in Bangladesh.

## 📌 Project Overview

The PAG System predicts, assesses, and mitigates disasters (floods, cyclones, droughts) using real-time data from:
- **BMD** (Bangladesh Meteorological Department)
- **BWDB** (Bangladesh Water Development Board)
- **IoT Sensors** (rainfall, soil moisture, water levels)
- **Satellite Imagery** (Sentinel/MODIS via OpenWeatherMap placeholder)

## 🏗️ Architecture

```
Data Sources → Kafka Cluster (3 Brokers) → Processing Layer → Decision Layer → Dashboard / Alerts
BMD / BWDB /    bmd_data, bwdb_data,      Isolation Forest   Risk Score      React + Leaflet
IoT / Satellite  sensor_data,             + LLM (Bangla)     + Policy Gen    + SMS/USSD
                 satellite_data
```

## 📦 Project Structure

```
pag-system/
├── data/
│   ├── prepare_data.py          # Train Isolation Forest model
│   ├── fetch_bmd_data.py        # BMD weather data fetcher
│   ├── fetch_bwdb_data.py       # BWDB river/polder data fetcher
│   ├── fetch_iot_data.py        # IoT sensor simulator
│   ├── fetch_satellite_data.py  # Satellite/OWM data fetcher
│   └── fetch_all_data.py        # Master script
├── kafka/
│   ├── producer.py              # Test data producer
│   ├── consumer.py              # Consumer + anomaly detection
│   └── requirements.txt         # Python dependencies
├── llm/
│   ├── mistral_api.py           # Mistral integration
│   ├── claude_api.py            # Claude integration
│   ├── gemini_api.py            # Gemini integration
│   └── bangla_prompt.py         # Universal LLM wrapper
├── dashboard/
│   ├── public/index.html        # HTML entry point
│   ├── src/App.jsx              # Main React app
│   ├── src/FullMapView.jsx      # Leaflet map view
│   ├── src/LowBandwidthView.jsx # Low-bandwidth text/SVG view
│   ├── src/SVGMap.jsx           # SVG fallback map
│   ├── src/index.js             # React entry point
│   └── package.json             # Node dependencies
├── decision_layer/
│   └── policy_generator.py      # Risk + ROI + policy recommendations
├── kafka-docker.yml             # Docker Compose for Kafka cluster
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites
- Docker
- Python 3.8+
- Node.js 18+
- API keys (optional): Mistral, Anthropic Claude, Google Gemini, OpenWeatherMap

### Step 1 — Start Kafka Cluster
```bash
docker-compose -f kafka-docker.yml up -d
```
Kafka UI: http://localhost:8080

### Step 2 — Install Python Dependencies
```bash
pip install -r kafka/requirements.txt
```

### Step 3 — Train Isolation Forest Model
```bash
python data/prepare_data.py
```

### Step 4 — Run Data Fetchers
```bash
python data/fetch_all_data.py
# or individually:
python data/fetch_bmd_data.py
python data/fetch_bwdb_data.py
python data/fetch_iot_data.py
python data/fetch_satellite_data.py
```

### Step 5 — Run Kafka Producer & Consumer
```bash
# Terminal 1
python kafka/producer.py
# Terminal 2
python kafka/consumer.py
```

### Step 6 — Run React Dashboard
```bash
cd dashboard
npm install
npm start
```
Dashboard: http://localhost:3000

## 🎯 Features

| Feature | Description |
|---|---|
| Real-Time Streaming | Kafka 3-broker cluster |
| Anomaly Detection | Isolation Forest |
| Bangla LLM Alerts | Mistral / Claude / Gemini |
| Low-Bandwidth Mode | SVG/text, ~50KB |
| Risk Assessment | Multi-hazard scoring |
| Policy Generator | DDM, UNO, NGO recommendations |
| ROI Analysis | Cost-benefit of anticipatory action |

## 🔧 Configuration

- **Kafka**: Edit `kafka-docker.yml` to change ports or replication.
- **LLM Keys**: Edit `llm/mistral_api.py`, `llm/claude_api.py`, `llm/gemini_api.py`.
- **Real APIs**: Replace placeholder URLs in `data/fetch_bmd_data.py` and `data/fetch_bwdb_data.py`.
- **Satellite**: Replace `your_openweathermap_api_key` in `data/fetch_satellite_data.py`.

## 📜 License

MIT License — Copyright (c) 2026 Nafiul Ahmad Rafi
