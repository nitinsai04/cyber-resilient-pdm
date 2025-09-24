import pandas as pd
import os

# Load dataset
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "rul_hrs.csv")
df = pd.read_csv(DATA_PATH)
sensor_cols = [col for col in df.columns if col.startswith("sensor_")]
