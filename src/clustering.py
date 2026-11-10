import os, sys, joblib, pandas as pd, numpy as np
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from src.preprocess import load_and_preprocess

MODELS_DIR = "models"

def perform_route_clustering(df=None, n_clusters=4, random_state=42):
    if df is None:
        df, _ = load_and_preprocess()

    route_agg = df.groupby(["Factory", "Region", "Product Name", "Ship Mode"]).agg(
        Order_Count=("Row ID", "count"),
        Avg_Lead_Time=("Lead Time", "mean"),
        Std_Lead_Time=("Lead Time", "std"),
        Avg_Distance=("Shipping Distance (miles)", "mean"),
        Total_Units=("Units", "sum"),
        Total_Sales=("Sales", "sum"),
        Avg_Profit_Margin=("Gross_Margin_Pct", "mean"),
    ).reset_index()

    route_agg["Std_Lead_Time"] = route_agg["Std_Lead_Time"].fillna(0.0)
    features = ["Avg_Lead_Time", "Std_Lead_Time", "Avg_Distance", "Total_Units", "Avg_Profit_Margin"]
    scaler = StandardScaler()
    scaled_feats = scaler.fit_transform(route_agg[features])

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    route_agg["Cluster"] = kmeans.fit_predict(scaled_feats)

    cluster_profiles = route_agg.groupby("Cluster").agg(
        Mean_Lead_Time=("Avg_Lead_Time", "mean"),
        Mean_Distance=("Avg_Distance", "mean"),
        Mean_Units=("Total_Units", "mean"),
        Mean_Margin=("Avg_Profit_Margin", "mean"),
        Route_Count=("Cluster", "count"),
    ).reset_index()

    def label_cluster(row):
        lt = row["Mean_Lead_Time"]
        units = row["Mean_Units"]
        dist = row["Mean_Distance"]
        if lt > cluster_profiles["Mean_Lead_Time"].quantile(0.65):
            return "Consistently Slow Route (Severe Bottleneck)"
        elif units > cluster_profiles["Mean_Units"].quantile(0.65):
            return "Congested High-Volume Lane"
        elif dist < cluster_profiles["Mean_Distance"].quantile(0.40):
            return "Fast Regional Corridor"
        else:
            return "Standard Interstate Route"

    cluster_profiles["Cluster_Label"] = cluster_profiles.apply(label_cluster, axis=1)
    label_dict = dict(zip(cluster_profiles["Cluster"], cluster_profiles["Cluster_Label"]))
    route_agg["Cluster_Label"] = route_agg["Cluster"].map(label_dict)

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(kmeans, os.path.join(MODELS_DIR, "route_kmeans.pkl"))
    joblib.dump(scaler, os.path.join(MODELS_DIR, "route_scaler.pkl"))
    route_agg.to_csv(os.path.join(MODELS_DIR, "route_clustering_results.csv"), index=False)
    return route_agg, cluster_profiles

def get_bottleneck_and_congested_routes(route_agg=None):
    if route_agg is None:
        res_file = os.path.join(MODELS_DIR, "route_clustering_results.csv")
        if os.path.exists(res_file):
            route_agg = pd.read_csv(res_file)
        else:
            route_agg, _ = perform_route_clustering()

    slow_routes = route_agg[route_agg["Cluster_Label"].str.contains("Slow|Bottleneck", case=False)].sort_values("Avg_Lead_Time", ascending=False)
    congested_lanes = route_agg[route_agg["Cluster_Label"].str.contains("Congested|Volume", case=False)].sort_values("Total_Units", ascending=False)
    return slow_routes, congested_lanes
