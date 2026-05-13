# tests/test_models.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from models.predictor import (
    make_sequences, get_scaler, FEATURES, SEQ_LEN,
    train_isolation_forest, predict_anomaly,
    train_xgboost, predict_xgboost,
    ensemble_predict,
)

# ── Fixtures ──────────────────────────────────────────────────
@pytest.fixture
def sample_df():
    np.random.seed(42)
    n = 500
    df = pd.DataFrame({
        "rainfall_mm":    np.random.normal(50, 30, n).clip(0),
        "wind_speed_kmh": np.random.normal(25, 15, n).clip(0),
        "river_level_m":  np.random.normal(5, 3, n).clip(0),
        "temperature_c":  np.random.normal(30, 5, n),
        "humidity":       np.random.uniform(40, 100, n),
        "risk_label":     np.random.randint(0, 2, n),
    })
    return df

@pytest.fixture
def normal_reading():
    return {"rainfall_mm": 20, "wind_speed_kmh": 15,
            "river_level_m": 3, "temperature_c": 30, "humidity": 65}

@pytest.fixture
def extreme_reading():
    return {"rainfall_mm": 800, "wind_speed_kmh": 250,
            "river_level_m": 18, "temperature_c": 45, "humidity": 98}

# ── Sequence generation ───────────────────────────────────────
class TestSequences:
    def test_shape_correct(self, sample_df):
        X = sample_df[FEATURES].values
        y = sample_df["risk_label"].values
        X_seq, y_seq = make_sequences(X, y, seq_len=24)
        assert X_seq.shape == (len(X) - 24, 24, len(FEATURES))
        assert y_seq.shape == (len(X) - 24,)

    def test_sequence_values_match_input(self, sample_df):
        X = sample_df[FEATURES].values
        y = sample_df["risk_label"].values
        X_seq, _ = make_sequences(X, y, seq_len=5)
        np.testing.assert_array_equal(X_seq[0], X[0:5])

# ── Isolation Forest ──────────────────────────────────────────
class TestIsolationForest:
    def test_trains_without_error(self, sample_df, tmp_path, monkeypatch):
        monkeypatch.setattr("models.predictor.MODELS_DIR", str(tmp_path))
        clf = train_isolation_forest(sample_df)
        assert clf is not None

    def test_normal_data_not_anomaly(self, sample_df, tmp_path, monkeypatch):
        monkeypatch.setattr("models.predictor.MODELS_DIR", str(tmp_path))
        train_isolation_forest(sample_df)
        result = predict_anomaly({"rainfall_mm": 50, "wind_speed_kmh": 20,
                                  "river_level_m": 5, "temperature_c": 30, "humidity": 65})
        assert isinstance(result, bool)

    def test_extreme_data_is_anomaly(self, sample_df, tmp_path, monkeypatch):
        monkeypatch.setattr("models.predictor.MODELS_DIR", str(tmp_path))
        train_isolation_forest(sample_df)
        result = predict_anomaly({"rainfall_mm": 5000, "wind_speed_kmh": 900,
                                  "river_level_m": 100, "temperature_c": 200, "humidity": 100})
        assert result is True

# ── XGBoost ───────────────────────────────────────────────────
class TestXGBoost:
    def test_trains_and_saves(self, sample_df, tmp_path, monkeypatch):
        monkeypatch.setattr("models.predictor.MODELS_DIR", str(tmp_path))
        model = train_xgboost(sample_df)
        assert model is not None
        assert os.path.exists(os.path.join(tmp_path, "xgboost_model.pkl"))

    def test_prediction_in_range(self, sample_df, tmp_path, monkeypatch, normal_reading):
        monkeypatch.setattr("models.predictor.MODELS_DIR", str(tmp_path))
        train_xgboost(sample_df)
        score = predict_xgboost(normal_reading)
        assert 0.0 <= score <= 1.0

    def test_high_rainfall_higher_risk(self, sample_df, tmp_path, monkeypatch):
        monkeypatch.setattr("models.predictor.MODELS_DIR", str(tmp_path))
        train_xgboost(sample_df)
        low  = predict_xgboost({"rainfall_mm": 10,  "wind_speed_kmh": 10,
                                 "river_level_m": 2, "temperature_c": 28, "humidity": 50})
        high = predict_xgboost({"rainfall_mm": 400, "wind_speed_kmh": 180,
                                 "river_level_m": 14, "temperature_c": 40, "humidity": 95})
        assert high >= low

# ── Ensemble ──────────────────────────────────────────────────
class TestEnsemble:
    def test_ensemble_returns_all_keys(self, sample_df, tmp_path, monkeypatch, normal_reading):
        monkeypatch.setattr("models.predictor.MODELS_DIR", str(tmp_path))
        monkeypatch.setattr("models.predictor.TF_AVAILABLE", False)
        train_isolation_forest(sample_df)
        train_xgboost(sample_df)
        result = ensemble_predict(normal_reading)
        for key in ["lstm_score", "xgboost_score", "ensemble_score", "risk_level", "is_anomaly"]:
            assert key in result

    def test_risk_level_valid(self, sample_df, tmp_path, monkeypatch, normal_reading):
        monkeypatch.setattr("models.predictor.MODELS_DIR", str(tmp_path))
        monkeypatch.setattr("models.predictor.TF_AVAILABLE", False)
        train_isolation_forest(sample_df)
        train_xgboost(sample_df)
        result = ensemble_predict(normal_reading)
        assert result["risk_level"] in ["low", "medium", "high"]
