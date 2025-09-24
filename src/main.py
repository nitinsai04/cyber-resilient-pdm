import numpy as np
import logging
from filterpy.kalman import KalmanFilter
from run_simulation import df, sensor_cols

# Setup logging
logging.basicConfig(filename="simulation.log", level=logging.INFO,
                    format="%(asctime)s - %(message)s")

def create_kf(dim_x=2, dim_z=1):
    kf = KalmanFilter(dim_x=dim_x, dim_z=dim_z)
    kf.x = np.array([0., 0.])            # initial state
    kf.F = np.array([[1., 1.],
                     [0., 1.]])          # state transition
    kf.H = np.array([[1., 0.]])          # measurement function
    kf.P *= 1000.0                       # covariance
    kf.R = 5                             # measurement noise
    kf.Q = np.array([[1., 0.],
                     [0., 1.]])          # process noise
    return kf

def run_simulation():
    kf = create_kf()
    alerts = []
    
    for i, row in df.iterrows():
        measurement = row[sensor_cols].mean()  # simple aggregation
        kf.predict()
        kf.update(measurement)

        # Example alert (if average sensor > 600)
        if measurement > 600:
            alert = f"High sensor average {measurement:.2f} at index {i}"
            alerts.append(alert)
            logging.warning(alert)

    # Write summary
    with open("simulation_summary.txt", "w") as f:
        f.write("Simulation complete.\n")
        f.write(f"Total data points processed: {len(df)}\n")
        f.write(f"Total alerts: {len(alerts)}\n")

if __name__ == "__main__":
    run_simulation()
    print("Simulation complete. Check simulation_summary.txt and simulation.log")
