# models/predictor.py
import numpy as np
import pandas as pd
import joblib
import os
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_squared_error
import xgboost as xgb

# TensorFlow/Keras for LSTM
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("⚠️  TensorFlow not installed — LSTM disabled. Run: pip install tensorflow")

MODELS_DIR = "models/saved"
os.makedirs(MODELS_DIR, exist_ok=True)

FEATURES = ["rainfall_mm", "wind_speed_kmh", "river_level_m", "temperature_c", "humidity"]
SEQ_LEN   = 24   # 24-hour lookback window for LSTM

# ── Scaler ───────────────────────────────────────────────────
def get_scaler(X: np.ndarray, save=True) -> MinMaxScaler:
    scaler = MinMaxScaler()
    scaler.fit(X)
    if save:
        joblib.dump(scaler, f"{MODELS_DIR}/scaler.pkl")
    return scaler

def load_scaler() -> MinMaxScaler:
    return joblib.load(f"{MODELS_DIR}/scaler.pkl")

# ── LSTM ─────────────────────────────────────────────────────
def build_lstm(input_shape):
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(32, return_sequences=False),
        Dropout(0.2),
        Dense(16, activation="relu"),
        Dense(1, activation="sigmoid"),   # risk probability 0-1
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model

def make_sequences(X: np.ndarray, y: np.ndarray, seq_len=SEQ_LEN):
    Xs, ys = [], []
    for i in range(len(X) - seq_len):
        Xs.append(X[i:i+seq_len])
        ys.append(y[i+seq_len])
    return np.array(Xs), np.array(ys)

def train_lstm(df: pd.DataFrame):
    if not TF_AVAILABLE:
        print("❌ TensorFlow not available — skipping LSTM training.")
        return None

    scaler = get_scaler(df[FEATURES].values)
    X_scaled = scaler.transform(df[FEATURES].values)
    y = (df["risk_label"].values if "risk_label" in df.columns
         else (df["rainfall_mm"].values > 200).astype(int))

    X_seq, y_seq = make_sequences(X_scaled, y)
    X_train, X_val, y_train, y_val = train_test_split(X_seq, y_seq, test_size=0.2, random_state=42)

    model = build_lstm((SEQ_LEN, len(FEATURES)))
    callbacks = [
        EarlyStopping(patience=5, restore_best_weights=True),
        ModelCheckpoint(f"{MODELS_DIR}/lstm_model.h5", save_best_only=True),
    ]
    model.fit(X_train, y_train, validation_data=(X_val, y_val),
              epochs=50, batch_size=32, callbacks=callbacks, verbose=1)

    loss, acc = model.evaluate(X_val, y_val, verbose=0)
    print(f"✅ LSTM trained — val_loss: {loss:.4f} | val_accuracy: {acc:.4f}")
    return model

def predict_lstm(data_point: dict) -> float:
    """Predict flood/cyclone risk (0–1) using LSTM."""
    if not TF_AVAILABLE:
        return -1.0
    model  = load_model(f"{MODELS_DIR}/lstm_model.h5")
    scaler = load_scaler()
    row = np.array([[data_point.get(f, 0) for f in FEATURES]])
    scaled = scaler.transform(row)
    seq = np.tile(scaled, (SEQ_LEN, 1)).reshape(1, SEQ_LEN, len(FEATURES))
    return float(model.predict(seq, verbose=0)[0][0])

# ── XGBoost ───────────────────────────────────────────────────
def train_xgboost(df: pd.DataFrame):
    y = (df["risk_label"].values if "risk_label" in df.columns
         else (df["rainfall_mm"].values > 200).astype(int))
    X = df[FEATURES].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X_train, y_train,
              eval_set=[(X_test, y_test)],
              verbose=False)

    y_pred = model.predict(X_test)
    print("✅ XGBoost trained:")
    print(classification_report(y_test, y_pred, target_names=["Low Risk", "High Risk"]))
    joblib.dump(model, f"{MODELS_DIR}/xgboost_model.pkl")
    return model

def predict_xgboost(data_point: dict) -> float:
    model = joblib.load(f"{MODELS_DIR}/xgboost_model.pkl")
    row = np.array([[data_point.get(f, 0) for f in FEATURES]])
    return float(model.predict_proba(row)[0][1])

# ── Isolation Forest (anomaly detection) ─────────────────────
def train_isolation_forest(df: pd.DataFrame):
    X = df[FEATURES].values
    clf = IsolationForest(contamination=0.05, random_state=42, n_estimators=200)
    clf.fit(X)
    joblib.dump(clf, f"{MODELS_DIR}/isolation_forest.pkl")
    print("✅ Isolation Forest trained and saved.")
    return clf

def predict_anomaly(data_point: dict) -> bool:
    clf = joblib.load(f"{MODELS_DIR}/isolation_forest.pkl")
    row = np.array([[data_point.get(f, 0) for f in FEATURES]])
    return clf.predict(row)[0] == -1   # True = anomaly

# ── Ensemble prediction ───────────────────────────────────────
def ensemble_predict(data_point: dict) -> dict:
    """
    Combine LSTM + XGBoost predictions.
    Weights: LSTM 40%, XGBoost 60% (XGBoost more reliable with sparse data).
    """
    xgb_score  = predict_xgboost(data_point)
    lstm_score = predict_lstm(data_point) if TF_AVAILABLE else xgb_score
    is_anomaly = predict_anomaly(data_point)

    if lstm_score < 0:          # TF not available
        ensemble_score = xgb_score
    else:
        ensemble_score = 0.4 * lstm_score + 0.6 * xgb_score

    level = "high" if ensemble_score >= 0.75 else "medium" if ensemble_score >= 0.45 else "low"
    return {
        "lstm_score":      round(lstm_score, 4),
        "xgboost_score":   round(xgb_score, 4),
        "ensemble_score":  round(ensemble_score, 4),
        "risk_level":      level,
        "is_anomaly":      is_anomaly,
    }

# ── Train all models ─────────────────────────────────────────
def train_all(csv_path="data/bangladesh_weather_data.csv"):
    df = pd.read_csv(csv_path)
    # Add synthetic risk labels for training if not present
    if "risk_label" not in df.columns:
        df["humidity"] = np.random.uniform(30, 100, len(df))
        df["risk_label"] = (
            (df["rainfall_mm"] > 150) | (df["river_level_m"] > 10)
        ).astype(int)

    print("\n📊 Training Isolation Forest...")
    train_isolation_forest(df)

    print("\n📊 Training XGBoost...")
    train_xgboost(df)

    print("\n📊 Training LSTM...")
    train_lstm(df)

    print("\n✅ All models trained successfully!")

if __name__ == "__main__":
    train_all()
