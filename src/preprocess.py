import math
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import joblib

from src.config import (
    FACTORY_COORDS,
    PRODUCT_FACTORY,
    REGION_COORDS,
    STATE_COORDS,
)

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    return R * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

def load_and_preprocess(filepath="data/Nassau_Candy_Distributor.csv"):
    if not os.path.exists(filepath):
        if os.path.exists("Nassau_Candy_Distributor.csv"):
            filepath = "Nassau_Candy_Distributor.csv"
        elif os.path.exists("../data/Nassau_Candy_Distributor.csv"):
            filepath = "../data/Nassau_Candy_Distributor.csv"

    df = pd.read_csv(filepath)
    df.columns = [c.strip() for c in df.columns]

    df["Order_Date_DT"] = pd.to_datetime(df["Order Date"], format="mixed", dayfirst=True)
    df["Ship_Date_DT"] = pd.to_datetime(df["Ship Date"], format="mixed", dayfirst=True)
    df["Lead Time"] = (df["Ship_Date_DT"] - df["Order_Date_DT"]).dt.total_seconds() / (24.0 * 3600.0)
    df = df[df["Lead Time"] > 0].copy()

    df["Factory"] = df["Product Name"].map(PRODUCT_FACTORY).fillna("Secret Factory")

    def get_dest_coords(row):
        state = str(row.get("State/Province", "")).strip()
        region = str(row.get("Region", "")).strip()
        if state in STATE_COORDS:
            return STATE_COORDS[state]
        if region in REGION_COORDS:
            return REGION_COORDS[region]
        return (39.8283, -98.5795)

    def calculate_distance(row):
        f_coords = FACTORY_COORDS.get(row["Factory"], (39.8283, -98.5795))
        d_coords = get_dest_coords(row)
        return haversine_distance(f_coords[0], f_coords[1], d_coords[0], d_coords[1])

    df["Shipping Distance (miles)"] = df.apply(calculate_distance, axis=1)
    df["Gross_Margin_Pct"] = np.where(df["Sales"] > 0, (df["Gross Profit"] / df["Sales"]) * 100.0, 0.0)
    df["Unit_Price"] = np.where(df["Units"] > 0, df["Sales"] / df["Units"], df["Sales"])
    df["Unit_Cost"] = np.where(df["Units"] > 0, df["Cost"] / df["Units"], df["Cost"])

    upper_lt = df["Lead Time"].quantile(0.995)
    lower_lt = df["Lead Time"].quantile(0.005)
    df = df[(df["Lead Time"] >= lower_lt) & (df["Lead Time"] <= upper_lt)].copy()

    categorical_cols = ["Product Name", "Factory", "Region", "Ship Mode", "Division"]
    encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[f"{col}_enc"] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    return df, encoders

def get_feature_matrix(df):
    feature_cols = [
        "Product Name_enc", "Factory_enc", "Region_enc", "Ship Mode_enc",
        "Division_enc", "Shipping Distance (miles)", "Units", "Cost", "Sales"
    ]
    return df[feature_cols].copy(), df["Lead Time"].copy(), feature_cols
