def fx(omega, friction):
    """
    Process model: update shaft speed (ω).
    dω/dt = (τm - τl - friction * ω) / J
    """
    from .constants import INERTIA, MOTOR_TORQUE, LOAD_TORQUE, DT
    domega = (MOTOR_TORQUE - LOAD_TORQUE - friction * omega) / INERTIA
    return omega + domega * DT


def hx(omega):
    """
    Measurement model: maps state to measurable output.
    For now, just return ω.
    """
    return omega
