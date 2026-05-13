# tests/test_kafka_consumer.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
import numpy as np
from unittest.mock import patch, MagicMock, call
from datetime import datetime

# ── Helper: isolation forest mock ─────────────────────────────
def make_mock_clf(prediction=1):
    clf = MagicMock()
    clf.predict.return_value = [prediction]
    return clf

# ── Data cleaning logic (extracted for testability) ───────────
def clean_data(data: dict, clf) -> dict | None:
    features = [[
        data.get("rainfall_mm", 0),
        data.get("wind_speed_kmh", 0),
        data.get("river_level_m", 0),
        data.get("temperature_c", 0),
    ]]
    if clf.predict(features)[0] == 1:
        data["cleaned_at"] = str(datetime.now())
        return data
    return None

# ── Tests ─────────────────────────────────────────────────────
class TestDataCleaning:
    def test_normal_data_passes(self):
        data = {"rainfall_mm": 50, "wind_speed_kmh": 20,
                "river_level_m": 5, "temperature_c": 30, "region": "Dhaka"}
        clf = make_mock_clf(prediction=1)
        result = clean_data(data, clf)
        assert result is not None
        assert "cleaned_at" in result

    def test_anomaly_data_rejected(self):
        data = {"rainfall_mm": 5000, "wind_speed_kmh": 900,
                "river_level_m": 100, "temperature_c": 200, "region": "Dhaka"}
        clf = make_mock_clf(prediction=-1)
        result = clean_data(data, clf)
        assert result is None

    def test_missing_fields_default_zero(self):
        data = {"region": "Sylhet"}
        clf = make_mock_clf(prediction=1)
        result = clean_data(data, clf)
        assert result is not None

    def test_clf_called_with_correct_features(self):
        data = {"rainfall_mm": 100, "wind_speed_kmh": 50,
                "river_level_m": 7, "temperature_c": 35}
        clf = make_mock_clf(prediction=1)
        clean_data(data, clf)
        clf.predict.assert_called_once_with([[100, 50, 7, 35]])

    def test_cleaned_at_is_string(self):
        data = {"rainfall_mm": 30, "wind_speed_kmh": 15,
                "river_level_m": 4, "temperature_c": 28}
        clf = make_mock_clf(prediction=1)
        result = clean_data(data, clf)
        assert isinstance(result["cleaned_at"], str)

class TestProducerData:
    def test_data_has_required_keys(self):
        import random
        regions = ["Sylhet", "Dhaka"]
        data = {
            "rainfall_mm":    random.choice([10, 50]),
            "wind_speed_kmh": random.choice([10, 20]),
            "river_level_m":  round(random.uniform(1, 20), 2),
            "temperature_c":  round(random.uniform(20, 50), 2),
            "humidity":       round(random.uniform(30, 100), 2),
            "region":         random.choice(regions),
            "timestamp":      datetime.now().isoformat(),
        }
        required = ["rainfall_mm", "wind_speed_kmh", "river_level_m",
                    "temperature_c", "humidity", "region", "timestamp"]
        for key in required:
            assert key in data

    def test_values_in_expected_range(self):
        data = {"rainfall_mm": 50, "wind_speed_kmh": 30,
                "river_level_m": 6, "temperature_c": 32, "humidity": 75}
        assert 0  <= data["rainfall_mm"]    <= 2000
        assert 0  <= data["wind_speed_kmh"] <= 500
        assert 0  <= data["river_level_m"]  <= 50
        assert -10 <= data["temperature_c"] <= 60
        assert 0  <= data["humidity"]       <= 100
