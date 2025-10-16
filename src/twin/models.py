# src/twin/models.py
"""
State update (fx) and measurement (hx) for the pump twin.
State x = [omega, theta, Tm]  (omega: rad/s, theta: degradation [0..], Tm: motor temperature °C)
Inputs u = dict(V, load_torque, valve)
Outputs y = dict(omega, temperature, flow, pressure, vibration)
"""
from __future__ import annotations
import numpy as np
from . import constants as C

def saturate(val, lo, hi):
    return max(lo, min(hi, val))

def fx(x, u, dt=C.DT):
    omega, theta, Tm = x
    V = u["V"]
    TL = u["load_torque"]
    valve = saturate(u["valve"], 0.0, 1.0)

    # Motor torque from voltage
    Tmtr = C.K_T * V

    # Effective viscous friction increases with degradation theta
    B_eff = C.B0 + C.K_DEG * theta

    # Rotational dynamics: J * domega = Tmtr - TL - B_eff*omega
    domega = (Tmtr - TL - B_eff * omega) / C.J

    # Degradation grows slowly with speed (proxy for wear)
    dtheta = C.ALPHA_WEAR * abs(omega)

    # Temperature dynamics: first-order to ambient plus heat from omega^2
    # dT = (T_env + K_HEAT*omega^2 - Tm) / tau
    dT = (C.T_ENV + C.K_HEAT * (omega ** 2) - Tm) / C.TAU_TH

    omega_next = omega + dt * domega
    theta_next = max(0.0, theta + dt * dtheta)
    Tm_next = Tm + dt * dT
    return np.array([omega_next, theta_next, Tm_next], dtype=float)

def cavitation_factor(omega, valve):
    # simple nonlinear penalty at very high speeds and partially closed valve
    severity = max(0.0, (omega - C.CAVITATION_OMEGA)) / C.CAVITATION_OMEGA
    restriction = (1.0 - valve)
    return 1.0 + 2.0 * severity * restriction  # >= 1

def hx(x, u):
    omega, theta, Tm = x
    valve = saturate(u["valve"], 0.0, 1.0)

    # Flow ~ K_Q * omega * valve / cavitation
    cav = cavitation_factor(omega, valve)
    flow = C.K_Q * omega * valve / cav  # L/s

    # Pressure ~ K_P * valve * omega  (toy relation)
    pressure = C.K_P * valve * omega * (1 - 0.2 * np.tanh((omega - 200)/200))

    # Vibration proxy ~ K_VIB * theta * omega^2
    vibration = C.K_VIB * theta * (omega ** 2)  # g (proxy)

    # Temperature is state Tm
    temperature = Tm

    return {
        "omega": float(omega),
        "temperature": float(temperature),
        "flow": float(flow),
        "pressure": float(pressure),
        "vibration": float(vibration),
    }
