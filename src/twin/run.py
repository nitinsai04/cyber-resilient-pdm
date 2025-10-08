# src/twin/run.py
from .pipeline import run_pipeline
from . import constants as C

if __name__ == "__main__":
    run_pipeline(steps=C.STEPS, dt=C.DT)
