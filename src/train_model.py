import os, sys, math, joblib, pandas as pd, numpy as np
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from src.preprocess import load_and_preprocess, get_feature_matrix

MODELS_DIR = "models"

def evaluate_model(name, model, X_test, y_test):
    preds = model.predict(X_test)
    rmse = math.sqrt(mean_squared_error(y_test, preds))
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    return {"Model": name, "RMSE": float(round(rmse, 2)), "MAE": float(round(mae, 2)), "R2": float(round(r2, 4)), "Fitted_Model": model}

def train_and_evaluate(data_path="data/Nassau_Candy_Distributor.csv"):
    os.makedirs(MODELS_DIR, exist_ok=True)
    df, encoders = load_and_preprocess(data_path)
    X, y, feature_cols = get_feature_matrix(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

    models_to_train = [
        ("Linear Regression (Baseline)", LinearRegression()),
        ("Random Forest Regressor", RandomForestRegressor(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1)),
        ("Gradient Boosting Regressor", GradientBoostingRegressor(n_estimators=150, learning_rate=0.08, max_depth=6, random_state=42)),
    ]

    records = []
    saved = {}
    for name, clf in models_to_train:
        clf.fit(X_train, y_train)
        ev = evaluate_model(name, clf, X_test, y_test)
        records.append({"Model": ev["Model"], "RMSE": ev["RMSE"], "MAE": ev["MAE"], "R2": ev["R2"]})
        saved[name] = clf

    eval_df = pd.DataFrame(records)
    eval_df.to_csv(os.path.join(MODELS_DIR, "model_results.csv"), index=False)
    best_model = saved["Linear Regression (Baseline)"]

    joblib.dump(saved["Linear Regression (Baseline)"], os.path.join(MODELS_DIR, "lr_model.pkl"))
    joblib.dump(saved["Random Forest Regressor"], os.path.join(MODELS_DIR, "rf_model.pkl"))
    joblib.dump(saved["Gradient Boosting Regressor"], os.path.join(MODELS_DIR, "gb_model.pkl"))
    joblib.dump(best_model, os.path.join(MODELS_DIR, "best_model.pkl"))
    joblib.dump(encoders, os.path.join(MODELS_DIR, "encoders.pkl"))
    joblib.dump(feature_cols, os.path.join(MODELS_DIR, "feature_cols.pkl"))
    return best_model, encoders, feature_cols, eval_df

if __name__ == "__main__":
    train_and_evaluate()
