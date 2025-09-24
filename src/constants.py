# Physical and simulation constants

INERTIA = 10.0          # J (kg*m^2), moment of inertia
MOTOR_TORQUE = 50.0     # τm (Nm), constant motor torque
LOAD_TORQUE = 20.0      # τl (Nm), opposing load
DT = 0.1                # Δt (s), timestep
SIMULATION_STEPS = 200  # total timesteps

# Safety thresholds
MAX_SPEED = 100.0       # rad/s, overspeed limit
MAX_TEMP = 80.0         # °C, example temperature threshold

# src/constants.py

# Threshold-based parameter
TEMP_THRESHOLD = 80.0  # °C

# Kalman Filter parameters
KF_PROCESS_VAR = 1e-5       # process noise variance
KF_MEASUREMENT_VAR = 0.1**2 # measurement noise variance
KF_INITIAL_TEMP = 25.0 