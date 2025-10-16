#!/usr/bin/env python3
"""
Industrial-style visualization for Digital Twin predictive maintenance.
-----------------------------------------------------------
✅ Trains on Helwig (pressure + flow)
✅ Tests on Twin (pressure + flow)
✅ Plots:
    - Pressure & Flow with Helwig ±2σ physical limits
    - ML fault probability (predict_proba) in separate panel
✅ Clean, industry-style layout with alert threshold line
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# === PATHS ===
HELWIG_DIR = Path("/Users/nitinsai/Documents/cyber-resilient-pdm/condition+monitoring+of+hydraulic+systems")
TWIN_CSV   = Path("/Users/nitinsai/Documents/cyber-resilient-pdm/data/generated_run_3000steps.csv")
OUTPUT_DIR = Path("/Users/nitinsai/Documents/cyber-resilient-pdm/outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")

# === LOAD HELWIG DATA ===
def load_helwig(helwig_dir):
    ps_files = [helwig_dir / f"PS{i}.txt" for i in range(1, 7)]
    fs_files = [helwig_dir / f"FS{i}.txt" for i in range(1, 3)]

    def read_avg(files):
        dfs = [pd.read_csv(f, sep="\t", header=None) for f in files]
        arr = np.stack([df.mean(axis=1) for df in dfs], axis=1)
        return arr.mean(axis=1)

    pressure = read_avg(ps_files)
    flow = read_avg(fs_files)

    profile = pd.read_csv(helwig_dir / "profile.txt", sep="\t", header=None)
    profile.columns = ["cooler", "valve", "pump", "accumulator", "stable"]

    df = pd.DataFrame({"pressure": pressure, "flow": flow})
    df = pd.concat([df, profile], axis=1)
    return df[df["stable"] == 0].reset_index(drop=True)


# === LOAD TWIN DATA ===
def load_twin(twin_csv):
    df = pd.read_csv(twin_csv)
    df = df[["pressure", "flow"]].dropna().reset_index(drop=True)
    return df


# === TRAIN MODEL ===
def train_model(df_helwig):
    X = df_helwig[["pressure", "flow"]]
    y = df_helwig["valve"]

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    clf = RandomForestClassifier(n_estimators=300, random_state=42)
    clf.fit(scaler.fit_transform(X_train), y_train)

    print("\n✅ Validation on Helwig dataset:")
    print(classification_report(y_val, clf.predict(scaler.transform(X_val))))
    return clf, scaler


# === INDUSTRIAL-STYLE VISUALIZATION ===
def visualize_industrial(df_twin, df_helwig, clf, scaler, output_dir, n_points=300):
    # Select random window of data for readability
    start = np.random.randint(500, len(df_twin) - n_points)
    df_twin = df_twin.iloc[start:start + n_points].reset_index(drop=True)
    print(f"🪄 Showing Twin samples {start}–{start + n_points}")

    # Compute Helwig thresholds
    mu_p, sd_p = df_helwig["pressure"].mean(), df_helwig["pressure"].std()
    mu_f, sd_f = df_helwig["flow"].mean(), df_helwig["flow"].std()
    thr_p_low, thr_p_high = mu_p - 2 * sd_p, mu_p + 2 * sd_p
    thr_f_low, thr_f_high = mu_f - 2 * sd_f, mu_f + 2 * sd_f

    # Compute ML predicted fault probability
    X_twin = df_twin[["pressure", "flow"]]
    X_twin_s = scaler.transform(X_twin)
    # predict_proba returns probability for each class (0,1,...)
    df_twin["fault_prob"] = clf.predict_proba(X_twin_s).max(axis=1)  # max prob = model confidence
    df_twin["pred_valve"] = clf.predict(X_twin_s)

    # Visualization setup
    fig, ax = plt.subplots(3, 1, figsize=(11, 7), sharex=True)
    t = df_twin.index

    # === Pressure Plot ===
    ax[0].fill_between(t, thr_p_low, thr_p_high, color="red", alpha=0.07, label="Helwig ±2σ Range")
    ax[0].plot(t, df_twin["pressure"], color="steelblue", lw=1.4, label="Twin Pressure")
    ax[0].set_ylabel("Pressure [bar]")
    ax[0].set_title("Pressure vs Helwig ±2σ Range with Predicted Fault Probability Overlay")
    ax[0].legend(loc="upper right")

    # === Flow Plot ===
    ax[1].fill_between(t, thr_f_low, thr_f_high, color="red", alpha=0.07, label="Helwig ±2σ Range")
    ax[1].plot(t, df_twin["flow"], color="darkorange", lw=1.4, label="Twin Flow")
    ax[1].set_ylabel("Flow [L/s]")
    ax[1].set_title("Flow vs Helwig ±2σ Range")
    ax[1].legend(loc="upper right")

    # === ML Probability Plot ===
    ax[2].plot(t, df_twin["fault_prob"], color="crimson", lw=1.6, label="Predicted Fault Probability")
    ax[2].axhline(0.7, color="gray", ls="--", lw=1, label="Alert Threshold (0.7)")
    ax[2].set_ylim(0, 1.05)
    ax[2].set_xlabel("Time Step")
    ax[2].set_ylabel("Fault Probability")
    ax[2].set_title("ML Predicted Fault Probability (Industrial Style)")
    ax[2].legend(loc="upper right")

    plt.tight_layout()
    out_path = output_dir / "twin_industrial_prediction.png"
    plt.savefig(out_path, dpi=300)
    plt.close()

    # === Summary ===
    print(f"\n📊 Industrial-style prediction visualization saved to: {out_path}")
    print(f"⚙️ Pressure mean ±2σ: [{thr_p_low:.2f}, {thr_p_high:.2f}] | Flow mean ±2σ: [{thr_f_low:.2f}, {thr_f_high:.2f}]")
    print(f"📈 Average fault probability: {df_twin['fault_prob'].mean():.3f}")
    print(f"🔍 Samples shown: {start}–{start + n_points}")


# === MAIN ===
if __name__ == "__main__":
    print("==> Loading Helwig dataset...")
    df_helwig = load_helwig(HELWIG_DIR)

    print("\n==> Training ML model...")
    clf, scaler = train_model(df_helwig)

    print("\n==> Loading Twin dataset...")
    df_twin = load_twin(TWIN_CSV)

    print("\n==> Generating industrial-style visualization...")
    visualize_industrial(df_twin, df_helwig, clf, scaler, OUTPUT_DIR, n_points=300)

    print("\n🎯 Done — ML probabilities, physical thresholds, and predictions shown cleanly.")
