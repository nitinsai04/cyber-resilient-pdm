# src/twin/pipeline.py
"""
Runs the full pipeline:
1) Generate synthetic multi-sensor data from the twin
2) Kalman filter each sensor (scalar KFs)
3) Compute thresholds (mean + k*sigma on warmup)
4) Log alerts to logs/alerts.txt and print summary
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
from filterpy.kalman import KalmanFilter
from . import constants as C
from .generator import run_generate

SENSOR_COLS = ["omega", "temperature", "flow", "pressure", "vibration"]

def create_scalar_kf(x0: float, q=1e-3, r=1e-2):
    kf = KalmanFilter(dim_x=1, dim_z=1)
    kf.x = np.array([[x0]], dtype=float)
    kf.F = np.array([[1.0]])
    kf.H = np.array([[1.0]])
    kf.P = np.array([[1.0]])
    kf.Q = np.array([[q]])
    kf.R = np.array([[r]])
    return kf

def run_pipeline(steps=C.STEPS, dt=C.DT, out_csv=None, alerts_path="logs/alerts.txt"):
    os.makedirs("logs", exist_ok=True)
    df, csv_path = run_generate(steps=steps, dt=dt, save_path=out_csv)

    # Build KFs per sensor using first finite value
    kfs = {}
    for s in SENSOR_COLS:
        init = df[s].dropna().iloc[0]
        kfs[s] = create_scalar_kf(init)

    # Warmup thresholds
    warm = df.iloc[:C.WARMUP_STEPS]
    thresholds = {}
    for s in SENSOR_COLS:
        mu = warm[s].mean(skipna=True)
        sd = warm[s].std(skipna=True)
        thresholds[s] = (mu, sd, mu + C.SIGMA_K * sd)

    # Scan & alert
    alerts = []
    with open(alerts_path, "w") as f:
        for i, row in df.iterrows():
            line_alerts = []
            for s in SENSOR_COLS:
                z = row[s]
                if np.isnan(z):
                    line_alerts.append(f"{i}:{s}:DROPOUT")
                    continue
                kfs[s].predict()
                kfs[s].update([z])
                est = float(kfs[s].x[0, 0])

                mu, sd, thr = thresholds[s]
                if sd > 0 and (abs(z - mu) > C.SIGMA_K * sd):
                    line_alerts.append(f"{i}:{s}:THRESH breach z={z:.3f} thr={thr:.3f}")
                # optional residual check:
                if abs(z - est) > max(3*sd, 1e-6):
                    line_alerts.append(f"{i}:{s}:RESID breach z-est={z-est:.3f}")

            if line_alerts:
                alerts.extend(line_alerts)
                f.write(" | ".join(line_alerts) + "\n")

    print("Simulation & monitoring complete.")
    print(f"Generated CSV : {csv_path}")
    print(f"Alerts log     : {alerts_path}")
    print(f"Total alerts   : {len(alerts)}")
    return csv_path, alerts_path, len(alerts)
