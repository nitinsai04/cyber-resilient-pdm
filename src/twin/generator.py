# src/twin/generator.py
"""
Generates multi-sensor timeseries from the twin by driving inputs (V, load_torque, valve)
over time and sampling hx() + sensor noise + optional anomaly injection.
Saves a CSV under data/.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from . import constants as C
from .models import fx, hx

RNG = np.random.default_rng(42)

def input_profile(t: int):
    """
    Define causal inputs over time (step tests, ramps, demand changes).
    You can customize this function freely.
    """
    # Voltage: ramp then hold with small jitter
    V = 24.0 + 2.0 * np.tanh((t - 200) / 200.0) + RNG.normal(0, 0.05)

    # Load torque: varies with a slow sinusoid (process variations)
    TL = 0.8 + 0.4 * (1 + np.sin(t / 180.0 * np.pi)) / 2.0

    # Valve: open mostly; periodic throttling events
    valve = 0.85 - 0.25 * (1 + np.sin((t - 500) / 250.0 * np.pi)) / 2.0
    valve = max(0.2, min(1.0, valve))
    return {"V": V, "load_torque": TL, "valve": valve}

def add_sensor_noise(y: dict):
    y = y.copy()
    y["omega"]      += RNG.normal(0.0, C.NOISE_OMEGA)
    y["temperature"]+= RNG.normal(0.0, C.NOISE_TEMP)
    y["flow"]       += RNG.normal(0.0, C.NOISE_FLOW)
    y["pressure"]   += RNG.normal(0.0, C.NOISE_PRESS)
    y["vibration"]  += RNG.normal(0.0, C.NOISE_VIB)
    return y

def maybe_inject_anomaly(y: dict, drift_state: dict):
    """
    Randomly injects spike, drift, dropout. Returns (y', labels)
    """
    labels = {"spike": 0, "drift": 0, "dropout": 0}

    # dropout
    if RNG.random() < C.P_DROPOUT:
        labels["dropout"] = 1
        # simulate missing read: set NaN
        for k in y.keys():
            y[k] = np.nan
        return y, labels

    # spike on a random channel
    if RNG.random() < C.P_SPIKE:
        labels["spike"] = 1
        k = RNG.choice(list(y.keys()))
        y[k] = y[k] * (1.0 + C.SPIKE_MULT * (1 if RNG.random() < 0.5 else -1))

    # drift (accumulates)
    if drift_state.get("active", False) or RNG.random() < C.P_DRIFT:
        drift_state["active"] = True
        labels["drift"] = 1
        for k in y.keys():
            drift_state[k] = drift_state.get(k, 0.0) + C.DRIFT_PER_STEP * (1 if RNG.random() < 0.5 else -1)
            if np.isfinite(y[k]):
                y[k] = y[k] + drift_state[k]

    return y, labels

def run_generate(steps=C.STEPS, dt=C.DT, x0=(0.0, 0.01, 25.0), save_path=None):
    x = np.array(x0, dtype=float)
    ts0 = datetime(2025, 1, 1, 0, 0, 0)
    rows = []
    drift_state = {}

    for t in range(steps):
        u = input_profile(t)
        x = fx(x, u, dt)
        y = hx(x, u)
        y = add_sensor_noise(y)
        y, lbl = maybe_inject_anomaly(y, drift_state)

        row = {
            "t": t,
            "timestamp": ts0 + timedelta(seconds=t*dt),
            "V": u["V"],
            "load_torque": u["load_torque"],
            "valve": u["valve"],
            "omega": y["omega"],
            "temperature": y["temperature"],
            "flow": y["flow"],
            "pressure": y["pressure"],
            "vibration": y["vibration"],
            "label_spike": lbl["spike"],
            "label_drift": lbl["drift"],
            "label_dropout": lbl["dropout"],
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    if save_path is None:
        save_path = f"data/generated_run_{steps}steps.csv"
    df.to_csv(save_path, index=False)
    return df, save_path
