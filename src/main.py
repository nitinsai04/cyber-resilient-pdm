# src/main.py

import random
from constants import TEMP_THRESHOLD
from kalman_filter import KalmanFilter

def simulate_sensor():
    """Generate noisy temperature readings around a rising trend."""
    base = 25
    for i in range(50):  # 50 readings
        temp = base + 0.5 * i + random.gauss(0, 2)  # add Gaussian noise
        yield temp

def main():
    kf = KalmanFilter()
    print("Starting simulation...\n")

    for reading in simulate_sensor():
        # --- Threshold check (old method) ---
        if reading >= TEMP_THRESHOLD:
            print(f"[Threshold Alert] Temp = {reading:.2f}°C exceeds {TEMP_THRESHOLD}°C")

        # --- Kalman Filter (new method) ---
        kf.predict()
        estimate = kf.update(reading)

        residual = abs(reading - estimate)
        if residual > 5:  # anomaly detection via deviation
            print(f"[KF Alert] Measured {reading:.2f}°C, KF estimate {estimate:.2f}°C (residual {residual:.2f})")

        print(f"Reading: {reading:.2f}°C | KF Estimate: {estimate:.2f}°C")

if __name__ == "__main__":
    main()
