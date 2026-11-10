import math, os, sys, joblib, pandas as pd, numpy as np
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config import FACTORY_COORDS, PRODUCT_FACTORY, REGION_COORDS, PRODUCT_DIVISION, FACTORY_DETAILS
from src.preprocess import haversine_distance

MODELS_DIR = "models"
BASE_FREIGHT_COST_PER_MILE_UNIT = 0.0015

class SimulationEngine:
    def __init__(self, models_dir=MODELS_DIR):
        self.models_dir = models_dir
        self.model = joblib.load(os.path.join(models_dir, "best_model.pkl"))
        self.encoders = joblib.load(os.path.join(models_dir, "encoders.pkl"))
        self.feature_cols = joblib.load(os.path.join(models_dir, "feature_cols.pkl"))

    def _encode_val(self, column, value):
        le = self.encoders[column]
        val_str = str(value)
        return int(le.transform([val_str])[0]) if val_str in le.classes_ else 0

    def predict_lead_time_single(self, product_name, factory_name, region, ship_mode, units=2, cost=3.0, sales=7.0):
        f_coords = FACTORY_COORDS.get(factory_name, (39.8283, -98.5795))
        r_coords = REGION_COORDS.get(region, (39.8283, -98.5795))
        dist_miles = haversine_distance(f_coords[0], f_coords[1], r_coords[0], r_coords[1])
        division = PRODUCT_DIVISION.get(product_name, "Chocolate")

        row = {
            "Product Name_enc": self._encode_val("Product Name", product_name),
            "Factory_enc": self._encode_val("Factory", factory_name),
            "Region_enc": self._encode_val("Region", region),
            "Ship Mode_enc": self._encode_val("Ship Mode", ship_mode),
            "Division_enc": self._encode_val("Division", division),
            "Shipping Distance (miles)": float(dist_miles),
            "Units": float(units),
            "Cost": float(cost),
            "Sales": float(sales),
        }
        X_eval = pd.DataFrame([row])[self.feature_cols]
        predicted_lead_time = float(self.model.predict(X_eval)[0])
        return max(predicted_lead_time, 1.0), dist_miles

    def simulate_all_factories(self, product_name, region="Interior", ship_mode="Standard Class", units=2, cost=3.0, sales=7.0):
        current_factory = PRODUCT_FACTORY.get(product_name, "Lot's O' Nuts")
        curr_lt, curr_dist = self.predict_lead_time_single(product_name, current_factory, region, ship_mode, units, cost, sales)
        curr_freight_cost = curr_dist * units * BASE_FREIGHT_COST_PER_MILE_UNIT
        baseline_gross_profit = sales - cost

        results = []
        for fac_name, coords in FACTORY_COORDS.items():
            pred_lt, pred_dist = self.predict_lead_time_single(product_name, fac_name, region, ship_mode, units, cost, sales)
            sim_freight_cost = pred_dist * units * BASE_FREIGHT_COST_PER_MILE_UNIT
            freight_delta = curr_freight_cost - sim_freight_cost
            lt_delta_days = curr_lt - pred_lt
            lt_reduction_pct = (lt_delta_days / curr_lt) * 100.0 if curr_lt > 0 else 0.0
            dist_delta = curr_dist - pred_dist
            adj_profit = baseline_gross_profit + freight_delta
            profit_stability_pct = (adj_profit / baseline_gross_profit) * 100.0 if baseline_gross_profit != 0 else 100.0
            dist_ratio = min(pred_dist, curr_dist) / max(pred_dist, curr_dist, 1.0)
            confidence_score = round(82.0 + (dist_ratio * 15.0), 1)

            results.append({
                "Factory": fac_name,
                "Is_Current": fac_name == current_factory,
                "Predicted_Lead_Time_Days": round(pred_lt, 1),
                "Lead_Time_Delta_Days": round(lt_delta_days, 1),
                "Lead_Time_Reduction_Pct": round(lt_reduction_pct, 2),
                "Distance_Miles": round(pred_dist, 0),
                "Distance_Delta_Miles": round(dist_delta, 0),
                "Est_Freight_Delta_USD": round(freight_delta, 2),
                "Est_Gross_Profit_USD": round(adj_profit, 2),
                "Profit_Impact_Stability_Pct": round(profit_stability_pct, 1),
                "Scenario_Confidence_Score": confidence_score,
                "Factory_City": FACTORY_DETAILS[fac_name]["city"],
                "Factory_State": FACTORY_DETAILS[fac_name]["state"],
            })
        return pd.DataFrame(results), current_factory, curr_lt, curr_dist
