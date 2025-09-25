import pandas as pd
import numpy as np
import logging
from models import create_kalman_filter
from constants import LOG_FILE, SUMMARY_FILE

def run_simulation(df, sensor_cols):
    # Setup logging
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                        format='%(asctime)s %(levelname)s:%(message)s')
    
    # Kalman filters for each sensor
    kfs = {sensor: create_kalman_filter(df[sensor].iloc[0]) for sensor in sensor_cols}
    
    # Compute thresholds (mean + 3*std)
    thresholds = {sensor: df[sensor].mean() + 3*df[sensor].std() for sensor in sensor_cols}
    
    total_alerts = 0
    
    for idx, row in df.iterrows():
        alerts_this_step = 0
        logging.info(f"Step {idx}: Timestamp={row['timestamp']}")
        for sensor in sensor_cols:
            kf = kfs[sensor]
            kf.predict()
            kf.update(np.array([[row[sensor]]]))
            filtered_value = kf.x[0][0]
            logging.info(f"{sensor}: raw={row[sensor]:.3f}, filtered={filtered_value:.3f}, threshold={thresholds[sensor]:.3f}")
            
            if filtered_value > thresholds[sensor]:
                alerts_this_step += 1
                total_alerts += 1
                logging.warning(f"ALERT! {sensor} exceeds threshold: {filtered_value:.3f} > {thresholds[sensor]:.3f}")
        
        if alerts_this_step == 0:
            logging.info("No alerts this step.")
    
    # Write summary
    with open(SUMMARY_FILE, "w") as f:
        f.write(f"Simulation complete.\n")
        f.write(f"Total data points processed: {len(df)}\n")
        f.write(f"Total alerts: {total_alerts}\n")

