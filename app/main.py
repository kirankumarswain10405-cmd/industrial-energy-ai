from fastapi import FastAPI
from app.data_loader import get_next_real_telemetry
from app.ml_engine import EnergyAIEngine

app = FastAPI(title="Industrial Energy AI API - Real Dataset")
engine = EnergyAIEngine()

@app.get("/")
def read_root():
    return {"status": "Online", "data_source": "Building Data Genome Project 2"}

@app.get("/api/v1/telemetry")
def get_telemetry():
    # Stream sequential telemetry from the real dataset
    data = get_next_real_telemetry()
    
    # Run scikit-learn anomaly detection on the real power reading
    raw_anomaly = engine.detect_anomaly(data["power_kw"])
    data["anomaly_detected"] = bool(raw_anomaly)
    return data

@app.post("/api/v1/optimize")
def optimize_loads(payload: dict):
    target = payload.get("target_power_kw", 120.0)
    current = payload.get("current_power_kw", 100.0)
    allocations = engine.optimize_operating_schedule(current, target)
    return {"status": "optimized", "allocations": allocations}
