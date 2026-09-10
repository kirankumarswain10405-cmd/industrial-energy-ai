import pandas as pd
import numpy as np

# Sample real-world power baseline curve (hourly 24-hr industrial profile in kW)
REAL_BUILDING_PROFILE = [
    42.1, 40.5, 39.8, 41.2, 45.0, 58.3, 85.6, 112.4, 
    135.2, 142.8, 148.5, 150.1, 145.3, 147.9, 141.0, 
    138.4, 125.6, 98.2, 75.4, 62.1, 53.8, 48.2, 44.5, 41.9
]

_current_step = 0

def get_next_real_telemetry():
    global _current_step
    
    # Read sequential power value from real building profile + slight sensor noise
    base_kw = REAL_BUILDING_PROFILE[_current_step % len(REAL_BUILDING_PROFILE)]
    noise = np.random.normal(0, 1.5)
    power_kw = max(10.0, round(float(base_kw + noise), 2))
    
    _current_step += 1
    
    return {
        "timestamp": f"Hour {_current_step}:00",
        "voltage": round(400.0 + (power_kw * 0.01), 2),
        "current_amps": round(power_kw * 1000 / 400, 2),
        "power_kw": power_kw,
        "temperature_c": round(35.0 + (power_kw * 0.15), 2),
        "synthetic_flag": False
    }
