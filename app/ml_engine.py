import numpy as np
from sklearn.ensemble import IsolationForest
from scipy.optimize import linprog

class EnergyAIEngine:
    def __init__(self):
        # Pre-train Isolation Forest on baseline energy bounds
        self.clf = IsolationForest(contamination=0.05, random_state=42)
        baseline_data = np.random.normal(loc=100.0, scale=15.0, size=(500, 1))
        self.clf.fit(baseline_data)

    def detect_anomaly(self, power_kw: float) -> bool:
        prediction = self.clf.predict([[power_kw]])
        return bool(prediction[0] == -1)

    def optimize_operating_schedule(self, current_power_kw: float, target_power_kw: float):
        """
        Uses SciPy Linear Programming to allocate power across 3 sub-systems:
        x1: HVAC, x2: Machinery, x3: Auxiliary Operations
        Minimizes power cost subject to operational capacity constraints.
        """
        # Objective function: Cost per kW for systems [HVAC, Machinery, Auxiliary]
        c = [0.12, 0.18, 0.10]

        # Inequality constraint: x1 + x2 + x3 <= target_power_kw
        A_ub = [[1, 1, 1]]
        b_ub = [target_power_kw]

        # Bounds for each sub-system (Min kW, Max kW)
        bounds = [(10, 50), (30, 100), (5, 30)]

        # Run linear optimization
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

        if res.success:
            return {
                "hvac_kw": round(res.x[0], 2),
                "machinery_kw": round(res.x[1], 2),
                "auxiliary_kw": round(res.x[2], 2),
                "estimated_cost_per_hr": round(res.fun, 2),
                "status": "Optimal load allocation found"
            }
        else:
            return {
                "hvac_kw": 0, "machinery_kw": 0, "auxiliary_kw": 0,
                "estimated_cost_per_hr": 0,
                "status": "Optimization constraint infeasible"
            }
