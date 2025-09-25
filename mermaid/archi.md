flowchart TD
    %% =======================
    %% Top-Level Simulation System
    %% =======================
    subgraph SIM["Cyber-Resilient Predictive Maintenance Digital Twin"]
        direction TB

        %% -----------------------
        %% Input & Constants Module
        %% -----------------------
        subgraph CONST["Constants Module (constants.py)"]
            direction LR
            INERTIA["INERTIA"]
            INITIAL_FRICTION["INITIAL_FRICTION"]
            MOTOR_TORQUE["MOTOR_TORQUE"]
            LOAD_TORQUE["LOAD_TORQUE"]
            VIBRATION_CONSTANT["VIBRATION_CONSTANT"]
            DT["Simulation Timestep (DT)"]
            SIM_STEPS["Simulation Steps (SIMULATION_STEPS)"]
        end

        %% -----------------------
        %% Models Module
        %% -----------------------
        subgraph MODEL["Process & Measurement Models (models.py)"]
            direction LR
            FX["Process Model fx()"]
            HX["Measurement Model hx()"]
        end

        %% -----------------------
        %% Simulation Runner
        %% -----------------------
        subgraph RUN["Simulation Runner (run_simulation.py / main.py)"]
            direction TB
            INIT["Initialize Simulation"]
            SENSOR_SIM["Simulate Sensor Readings"]
            APPLY_MODELS["Apply fx() & hx()"]
            LOGGING["Log Data & Alerts"]
            KF_MODULE["Kalman Filter Estimation (optional)"]
            OVER_TEMP["Check Thresholds / Stop Simulation if needed"]
        end

        %% -----------------------
        %% Connections
        %% -----------------------
        CONST --> MODEL
        MODEL --> RUN
        INIT --> SENSOR_SIM
        SENSOR_SIM --> APPLY_MODELS
        APPLY_MODELS --> LOGGING
        APPLY_MODELS --> KF_MODULE
        LOGGING --> OVER_TEMP
        KF_MODULE --> OVER_TEMP
    end

    %% =======================
    %% Notes / Annotations
    %% =======================
    classDef module fill:#f9f,stroke:#333,stroke-width:2px;
    class CONST,MODEL,RUN module;
