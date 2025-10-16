"""
Physical and simulation parameters for the data-generating Digital Twin.
Tuned to align magnitude with Helwig hydraulic dataset (≈50 bar, 7 L/s).
"""

# --- Mechanical / thermal ---
J = 0.08                 # moment of inertia [kg*m^2]
B0 = 0.02                # base viscous friction [N*m*s/rad]
K_DEG = 0.15             # added friction per unit degradation theta [-]
K_T = 0.08               # motor torque constant [N*m/V]
TAU_TH = 15.0            # thermal time constant [s]
T_ENV = 25.0             # ambient temperature [°C]
K_HEAT = 0.002           # heating coeff (~omega^2 contribution to temp) [°C/(rad/s)^2]

# --- Hydraulics (scaled to Helwig dataset) ---
K_Q = 0.36               # ↑ flow proportionality [L/s per (rad/s)]
K_P = 2.0                # ↑ pressure proportionality [bar per (rad/s * valve)]
CAVITATION_OMEGA = 200.0 # omega scale where cavitation risk starts

# --- Vibration proxy ---
K_VIB = 0.4              # vibration ~ K_VIB * theta * omega^2 [g]

# --- Wear / degradation ---
ALPHA_WEAR = 1e-5        # slow wear per timestep scaled by omega

# --- Discrete-time sim ---
DT = 0.1                 # seconds per step
STEPS = 3000             # default number of steps

# --- Noise (sensor) ---
NOISE_TEMP = 0.05
NOISE_FLOW = 0.02
NOISE_PRESS = 0.03
NOISE_VIB = 0.01
NOISE_OMEGA = 0.05

# --- Anomaly injection (probabilities per step) ---
P_SPIKE = 0.002          # rare large spike
P_DRIFT = 0.001          # slow drift chance start
P_DROPOUT = 0.001        # missing data

# --- Spike/drift magnitudes ---
SPIKE_MULT = 3.0
DRIFT_PER_STEP = 0.002

# --- Thresholding (alert rules) ---
WARMUP_STEPS = 200       # compute mean/std on this window
SIGMA_K = 3.0            # mean + k*std
