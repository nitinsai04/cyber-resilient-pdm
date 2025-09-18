# src/simulation/__init__.py
"""
Simulation package for Cyber-Resilient Predictive Maintenance.

This package provides:
- Constants (physical + simulation parameters)
- Models (process + measurement models)
- Run function to execute the digital twin simulation
"""

# Package metadata
__version__ = "0.1.0"
__author__ = "Team Cyber-Resilient-PDM"

# Expose key functions and constants for easy imports
from .constants import (
    INERTIA,
    INITIAL_FRICTION,
    MOTOR_TORQUE,
    LOAD_TORQUE,
    VIBRATION_CONSTANT,
    DT,
    SIMULATION_STEPS,
)

from .models import fx, hx
from .run_simulation import run

__all__ = [
    # constants
    "INERTIA", "INITIAL_FRICTION", "MOTOR_TORQUE", "LOAD_TORQUE",
    "VIBRATION_CONSTANT", "DT", "SIMULATION_STEPS",
    # models
    "fx", "hx",
    # main runner
    "run",
]
