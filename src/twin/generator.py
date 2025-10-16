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

# ===========================================================
#  INPUT PROFILE FUNCTION — defines system control inputs
# ===========================================================
def input_profile(t: int):
    """
    Define causal inputs over time (step tests, ramps, demand changes).
    You can customize this function freely.
    """
    # --- Voltage: ramp + random duty-cycle load modulation ---
    V = 24.0 + 2.0 * np.tanh((t - 200) / 200.0)
    if t % 400 > 300:  # simulate load surge every ~40s
        V += 1.0
    V += RNG.normal(0, 0.1)

    # --- Load torque: varies with a slow sinusoid (process variations) ---
    TL = 0.8 + 0.4 * (1 + np.sin(t / 180.0 * np.pi)) / 2.0

    # --- Valve: random throttling cycles (simulate actuator wear) ---
    base = 0.8 - 0.3 * (1 + np.sin((t - 500) / 180.0 * np.pi)) / 2.0
    valve = base + RNG.normal(0, 0.05)
    valve = np.clip(valve, 0.2, 1.0)

    # ✅ Return the control input dictionary
    return {"V": V, "load_torque": TL, "valve": valve}


# ===========================================================
#  SENSOR NOISE + ANOMALY INJECTION HELPERS
# ===========================================================
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
        for k in y.keys():
            y[k] = np.nan
        return y, labels

    # spike on a random channel
    if RNG.random() < C.P_SPIKE:
        labels["spike"] = 1
        k = RNG.choice(list(y.keys()))
        y[k] = y[k] * (1.0 + C.SPIKE_MULT * (1 if RNG.random() < 0.5 else -1))

    # drift (accumulates slowly)
    if drift_state.get("active", False) or RNG.random() < C.P_DRIFT:
        drift_state["active"] = True
        labels["drift"] = 1
        for k in y.keys():
            drift_state[k] = drift_state.get(k, 0.0) + C.DRIFT_PER_STEP * (1 if RNG.random() < 0.5 else -1)
            if np.isfinite(y[k]):
                y[k] = y[k] + drift_state[k]

    return y, labels


# ===========================================================
#  MAIN SIMULATION LOOP
# ===========================================================
def run_generate(steps=C.STEPS, dt=C.DT, x0=(0.0, 0.01, 25.0), save_path=None):
    """
    Main Digital Twin data generation loop.
    Simulates a hydraulic pump with dynamic inputs, realistic sensor drift,
    and a mid-run valve fault for realism.
    """
    x = np.array(x0, dtype=float)
    ts0 = datetime(2025, 1, 1, 0, 0, 0)
    rows = []
    drift_state = {}

    global BASE_DRIFT
    BASE_DRIFT = 0.0

    for t in range(steps):
        # === Input generation with semi-random behavior ===
        u = input_profile(t)

        # --- Introduce a mid-run fault episode (valve obstruction) ---
        if 1500 < t < 1800:
            u["valve"] *= 0.55  # partial blockage (reduces flow & pressure)

        # --- Simulate random load disturbances (external torque variation) ---
        if t % 500 > 400:
            u["load_torque"] *= 1.2  # short bursts of increased load

        # === System state update ===
        x = fx(x, u, dt)
        y = hx(x, u)

        # === Shared drift (simulates calibration drift or slow temp change) ===
        BASE_DRIFT += np.random.normal(0, 0.0005)
        for k in ["omega", "temperature", "flow", "pressure"]:
            y[k] += BASE_DRIFT * np.random.uniform(0.05, 0.2)

        # === Sensor noise and anomalies ===
        y = add_sensor_noise(y)
        y, lbl = maybe_inject_anomaly(y, drift_state)

        # === Record data point ===
        row = {
            "t": t,
            "timestamp": ts0 + timedelta(seconds=t * dt),
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

    # === Save dataset ===
    df = pd.DataFrame(rows)
    if save_path is None:
        save_path = f"data/generated_run_{steps}steps.csv"
    df.to_csv(save_path, index=False)

    print(f"\n💾 Simulation complete — {len(df)} steps generated.")
    print(f"📁 Data saved to: {save_path}")
    print("⚙️  Includes: valve fault (t=1500–1800), load spikes, correlated drift.\n")

    return df, save_path
