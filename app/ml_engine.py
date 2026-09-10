import numpy as np
from sklearn.ensemble import IsolationForest
from scipy.optimize import minimize

class EnergyAIEngine:
    def __init__(self):
        baseline_data = np.random.normal(loc=80, scale=15, size=(500, 1))
        self.anomaly_detector = IsolationForest(contamination=0.05, random_state=42)
        self.anomaly_detector.fit(baseline_data)

    def detect_anomaly(self, power_kw: float) -> bool:
        pred = self.anomaly_detector.predict([[power_kw]])
        return pred[0] == -1

    def optimize_operating_schedule(self, current_power: float, target_power: float):
        def objective(x):
            costs = [0.12, 0.15, 0.10]
            return sum(x[i] * costs[i] for i in range(3))

        constraints = ({'type': 'eq', 'fun': lambda x: sum(x) - target_power})
        bounds = [(10, 100), (10, 100), (10, 100)]
        initial_guess = [target_power / 3] * 3

        res = minimize(objective, initial_guess, bounds=bounds, constraints=constraints)
        if res.success:
            return {
                "chiller_1_kw": round(res.x[0], 2),
                "chiller_2_kw": round(res.x[1], 2),
                "chiller_3_kw": round(res.x[2], 2)
            }
        return {"chiller_1_kw": target_power/3, "chiller_2_kw": target_power/3, "chiller_3_kw": target_power/3}
