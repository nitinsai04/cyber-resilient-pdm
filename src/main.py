import pandas as pd
from constants import DATA_FILE
from run_simulation import run_simulation

def main():
    # Load dataset
    df = pd.read_csv(DATA_FILE)
    sensor_cols = [col for col in df.columns if col.startswith("sensor_")]
    
    # Run simulation with logging
    run_simulation(df, sensor_cols)
    print("Simulation complete. Check simulation_summary.txt and simulation.log")

if __name__ == "__main__":
    main()
