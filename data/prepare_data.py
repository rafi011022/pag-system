# data/prepare_data.py
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

os.makedirs("data", exist_ok=True)

np.random.seed(42)
n_samples = 10000

data = {
    "rainfall_mm": np.concatenate([
        np.random.normal(50, 20, int(n_samples * 0.9)),
        np.random.normal(500, 100, int(n_samples * 0.05)),
        np.random.normal(1000, 200, int(n_samples * 0.05))
    ]),
    "wind_speed_kmh": np.concatenate([
        np.random.normal(20, 10, int(n_samples * 0.9)),
        np.random.normal(150, 30, int(n_samples * 0.05)),
        np.random.normal(300, 50, int(n_samples * 0.05))
    ]),
    "river_level_m": np.concatenate([
        np.random.normal(5, 2, int(n_samples * 0.9)),
        np.random.normal(15, 3, int(n_samples * 0.05)),
        np.random.normal(30, 5, int(n_samples * 0.05))
    ]),
    "temperature_c": np.concatenate([
        np.random.normal(30, 5, int(n_samples * 0.9)),
        np.random.normal(50, 10, int(n_samples * 0.05)),
        np.random.normal(100, 20, int(n_samples * 0.05))
    ]),
    "region": np.random.choice(["Sylhet", "Dhaka", "Chittagong", "Kurigram", "Sunamganj"], n_samples),
}

df = pd.DataFrame(data)
df.to_csv("data/bangladesh_weather_data.csv", index=False)

features = ["rainfall_mm", "wind_speed_kmh", "river_level_m", "temperature_c"]
X = df[features]

clf = IsolationForest(contamination=0.05, random_state=42)
clf.fit(X)

joblib.dump(clf, "data/isolation_forest_bangladesh.pkl")

print("✅ Data and model saved successfully!")
print("Data saved to: data/bangladesh_weather_data.csv")
print("Model saved to: data/isolation_forest_bangladesh.pkl")
