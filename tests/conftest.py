# tests/conftest.py
import pytest
import numpy as np
import pandas as pd

@pytest.fixture(scope="session")
def sample_weather_df():
    np.random.seed(0)
    n = 300
    return pd.DataFrame({
        "rainfall_mm":    np.random.normal(60, 40, n).clip(0),
        "wind_speed_kmh": np.random.normal(30, 20, n).clip(0),
        "river_level_m":  np.random.normal(6, 4, n).clip(0),
        "temperature_c":  np.random.normal(30, 6, n),
        "humidity":       np.random.uniform(40, 100, n),
        "risk_label":     np.random.randint(0, 2, n),
        "region":         np.random.choice(["Sylhet", "Dhaka", "Chittagong"], n),
    })

@pytest.fixture
def flood_data():
    return {"rainfall_mm": 280, "wind_speed_kmh": 30,
            "river_level_m": 13, "temperature_c": 32, "humidity": 90}

@pytest.fixture
def cyclone_data():
    return {"rainfall_mm": 120, "wind_speed_kmh": 210,
            "river_level_m": 5, "temperature_c": 35, "humidity": 85}

@pytest.fixture
def safe_data():
    return {"rainfall_mm": 15, "wind_speed_kmh": 10,
            "river_level_m": 2, "temperature_c": 28, "humidity": 55}
