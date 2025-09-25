import numpy as np
from filterpy.kalman import KalmanFilter

def create_kalman_filter(initial_value=0.0):
    kf = KalmanFilter(dim_x=1, dim_z=1)
    kf.x = np.array([[initial_value]])    # initial state
    kf.P = np.array([[1]])               # initial covariance
    kf.F = np.array([[1]])               # state transition
    kf.H = np.array([[1]])               # measurement function
    kf.R = np.array([[0.1]])             # measurement noise
    kf.Q = np.array([[0.01]])            # process noise
    return kf
