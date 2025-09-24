# src/kalman_filter.py

from constants import KF_PROCESS_VAR, KF_MEASUREMENT_VAR, KF_INITIAL_TEMP

class KalmanFilter:
    def __init__(self, process_var=KF_PROCESS_VAR, measurement_var=KF_MEASUREMENT_VAR):
        # Initial estimates
        self.x = KF_INITIAL_TEMP
        self.P = 1.0  # initial error covariance

        # Noise parameters
        self.Q = process_var
        self.R = measurement_var

    def predict(self):
        # Prediction step (identity model in 1D)
        self.P += self.Q
        return self.x

    def update(self, z):
        # Kalman Gain
        K = self.P / (self.P + self.R)
        # Update state with measurement
        self.x = self.x + K * (z - self.x)
        # Update error covariance
        self.P = (1 - K) * self.P
        return self.x
