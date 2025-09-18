import logging
from .constants import SIMULATION_STEPS, DT, MAX_SPEED, MAX_TEMP
from .models import fx, hx

# configure logging
logging.basicConfig(filename="simulation.log", level=logging.INFO, filemode="w")

def run():
    omega = 0.0          # initial shaft speed
    friction = 0.01      # initial friction
    temp = 25.0          # initial temp (°C)

    for step in range(SIMULATION_STEPS):
        # update system dynamics
        omega = fx(omega, friction)
        measured = hx(omega)

        # simple temp model: proportional to speed
        temp += 0.01 * measured  

        # --- SAFETY CHECKS ---
        if measured > MAX_SPEED:
            logging.warning(f"Step {step}: Overspeed detected! ω={measured:.2f}")
            print(f"⚠️ Simulation stopped at step {step}: Overspeed")
            break

        if temp > MAX_TEMP:
            logging.warning(f"Step {step}: Overtemperature detected! T={temp:.2f}")
            print(f"⚠️ Simulation stopped at step {step}: Overtemperature")
            break

        # log normal behavior
        logging.info(f"Step {step}: ω={measured:.2f}, Temp={temp:.2f}")
