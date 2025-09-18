# cyber-resilient-pdm
This is a new line in test-branch
# Cyber-Resilient Predictive Maintenance - Simulation Code

This repository contains the foundational simulation for a cyber-resilient predictive maintenance digital twin. The code is modularized into several Python files under the `src/` directory. Below is a detailed explanation of each file:

---

## `constants.py`
Holds all the physical properties of the pump and simulation parameters. Centralizing these values makes it easy to tweak the simulation without changing the logic in models or the main runner.

**Key content:**
- `INERTIA`, `MOTOR_TORQUE`, `LOAD_TORQUE`: Pump dynamics parameters.
- `INITIAL_FRICTION`, `VIBRATION_CONSTANT`: Friction and vibration-related constants.
- `DT`, `SIMULATION_STEPS`: Time step and total number of simulation iterations.

---

## `models.py`
Contains the core mathematical models of the system.

**Key functions:**
- `fx(x, dt)`: Process model that updates the pump state (`omega`, `theta`) based on current state, torque, friction, and a small stochastic term for degradation.
- `hx(x)`: Measurement model that simulates sensor outputs (tachometer for speed, accelerometer for vibration) from the current pump state.

This separation allows clear distinction between system dynamics and sensor modeling.

---

## `run_simulation.py`
Main script that runs the digital twin simulation.

**Key responsibilities:**
- Configures the Unscented Kalman Filter (UKF) using parameters from `constants.py`.
- Initializes true and estimated states.
- Runs the simulation loop:
  - Updates the true pump state using `fx`.
  - Simulates sensor measurements using `hx`.
  - Performs UKF predict and update steps.
  - Logs anomalies or threshold violations (e.g., overtemperature).
- Plots the results showing true vs estimated states.

This is the file to run the simulation (`python -m src.run_simulation`) and observe the outputs.

---

## `main.py`
(Optional/placeholder) Entry point for integrating the simulation with other modules or a dashboard. Currently can be used to call `run()` from `run_simulation.py`.

---

## `__init__.py`
Marks the `src` directory as a Python package and exposes key components for easier imports. Provides:
- Metadata (`__version__`, `__author__`)
- Easy access to constants, models, and the `run` function for modular usage.

---

### Summary
- **`constants.py`** → Physical & simulation parameters  
- **`models.py`** → Process & measurement models  
- **`run_simulation.py`** → Main simulation driver  
- **`main.py`** → Optional integration entry point  
- **`__init__.py`** → Package metadata and convenient imports

---

This structure ensures modularity, maintainability, and easy collaboration for team members.
