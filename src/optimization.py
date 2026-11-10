import os, sys, pandas as pd, numpy as np
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config import PRODUCT_FACTORY, FACTORY_COORDS, REGION_COORDS
from src.simulation import SimulationEngine

class OptimizerRecommendationEngine:
    def __init__(self, simulation_engine=None):
        self.sim_engine = simulation_engine if simulation_engine is not None else SimulationEngine()

    def rank_factories(self, sim_df, priority_weight=0.5, risk_tolerance="Balanced"):
        df = sim_df.copy()
        max_lt_red, min_lt_red = df["Lead_Time_Reduction_Pct"].max(), df["Lead_Time_Reduction_Pct"].min()
        df["Norm_Speed"] = 50.0 if max_lt_red == min_lt_red else ((df["Lead_Time_Reduction_Pct"] - min_lt_red) / (max_lt_red - min_lt_red)) * 100.0
        max_prof, min_prof = df["Est_Freight_Delta_USD"].max(), df["Est_Freight_Delta_USD"].min()
        df["Norm_Profit"] = 50.0 if max_prof == min_prof else ((df["Est_Freight_Delta_USD"] - min_prof) / (max_prof - min_prof)) * 100.0

        risk_multipliers = {"Conservative": 1.5, "Balanced": 1.0, "Aggressive": 0.5}
        r_mult = risk_multipliers.get(risk_tolerance, 1.0)
        dist_pen = np.where(df["Distance_Delta_Miles"] < 0, np.abs(df["Distance_Delta_Miles"]) / 100.0, 0.0)
        conf_pen = (100.0 - df["Scenario_Confidence_Score"]) * 0.4
        df["Risk_Score"] = (dist_pen + conf_pen) * r_mult

        w = float(priority_weight)
        df["Composite_Score"] = (1.0 - w) * df["Norm_Speed"] + w * df["Norm_Profit"] - df["Risk_Score"]

        def assign_risk_badge(row):
            if row["Lead_Time_Reduction_Pct"] < -5.0 or row["Distance_Delta_Miles"] < -500:
                return "HIGH RISK (Distance/Time Expansion)"
            elif row["Est_Freight_Delta_USD"] < -0.5:
                return "MODERATE RISK (Freight Margin Erosion)"
            elif row["Lead_Time_Reduction_Pct"] > 10.0 and row["Est_Freight_Delta_USD"] >= 0:
                return "LOW RISK (High Efficiency Opportunity)"
            return "NEUTRAL / BASELINE"

        df["Risk_Classification"] = df.apply(assign_risk_badge, axis=1)
        df = df.sort_values(by="Composite_Score", ascending=False).reset_index(drop=True)
        df["Rank"] = df.index + 1
        return df

    def generate_global_recommendations(self, products=None, regions=None, priority_weight=0.5, risk_tolerance="Balanced", top_n=5):
        products = products or list(PRODUCT_FACTORY.keys())
        regions = regions or list(REGION_COORDS.keys())
        recs, total, beneficial = [], 0, 0

        for prod in products:
            curr_fac = PRODUCT_FACTORY[prod]
            for reg in regions:
                total += 1
                sim_df, _, _, _ = self.sim_engine.simulate_all_factories(product_name=prod, region=reg)
                ranked_df = self.rank_factories(sim_df, priority_weight, risk_tolerance)
                alt_options = ranked_df[ranked_df["Factory"] != curr_fac]
                if not alt_options.empty:
                    best_alt = alt_options.iloc[0]
                    curr_row = ranked_df[ranked_df["Factory"] == curr_fac].iloc[0]
                    if best_alt["Composite_Score"] > curr_row["Composite_Score"] and (best_alt["Lead_Time_Reduction_Pct"] > 2.0 or best_alt["Est_Freight_Delta_USD"] > 0.2):
                        beneficial += 1
                        recs.append({
                            "Product": prod,
                            "Destination_Region": reg,
                            "Current_Factory": curr_fac,
                            "Recommended_Factory": best_alt["Factory"],
                            "Lead_Time_Reduction_Pct": best_alt["Lead_Time_Reduction_Pct"],
                            "Days_Saved": best_alt["Lead_Time_Delta_Days"],
                            "Miles_Saved": best_alt["Distance_Delta_Miles"],
                            "Est_Freight_Savings_USD": best_alt["Est_Freight_Delta_USD"],
                            "Confidence_Score": best_alt["Scenario_Confidence_Score"],
                            "Risk_Level": best_alt["Risk_Classification"],
                            "Composite_Score": round(best_alt["Composite_Score"], 2),
                        })
        rec_df = pd.DataFrame(recs)
        top_recs = rec_df.sort_values(by="Composite_Score", ascending=False).reset_index(drop=True).head(top_n) if not rec_df.empty else pd.DataFrame()
        cov = (beneficial / total) * 100.0 if total > 0 else 0.0
        return top_recs, rec_df, round(cov, 1)
