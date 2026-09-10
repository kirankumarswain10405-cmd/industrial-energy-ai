import numpy as np
from datetime import datetime

def generate_telemetry_point():
    now = datetime.now()
    hour = now.hour
    base_load = 120.0 if 8 <= hour <= 18 else 40.0
    noise = np.random.normal(0, 5.0)
    is_anomaly = np.random.rand() < 0.05
    power_kw = base_load + noise + (80.0 if is_anomaly else 0.0)
    
    return {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "voltage": round(float(np.random.normal(400, 2.0)), 2),
        "current_amps": round(float(power_kw * 1000 / 400), 2),
        "power_kw": round(float(power_kw), 2),
        "temperature_c": round(float(np.random.normal(65 if 8 <= hour <= 18 else 30, 3.0)), 2),
        "synthetic_flag": is_anomaly
    }
