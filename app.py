import os, sys, math, joblib, pandas as pd, numpy as np
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from src.config import FACTORY_COORDS, FACTORY_DETAILS, PRODUCT_FACTORY, REGION_COORDS, PRODUCT_DIVISION
from src.preprocess import load_and_preprocess
from src.simulation import SimulationEngine, BASE_FREIGHT_COST_PER_MILE_UNIT
from src.optimization import OptimizerRecommendationEngine
from src.clustering import get_bottleneck_and_congested_routes
from src.utils import build_geospatial_network_map

st.set_page_config(
    page_title="Nassau Candy | Factory Reallocation & Optimization",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Guard against browser extension errors (like spoofer.js)
components.html("""
<script>
window.addEventListener('error', function(e) {
    if (e && (e.filename && e.filename.indexOf('spoofer') !== -1 || e.message && e.message.indexOf('spoofer') !== -1)) {
        e.stopImmediatePropagation();
        e.preventDefault();
        return true;
    }
}, true);
try {
    if (window.parent && window.parent !== window) {
        window.parent.addEventListener('error', function(e) {
            if (e && (e.filename && e.filename.indexOf('spoofer') !== -1 || e.message && e.message.indexOf('spoofer') !== -1)) {
                e.stopImmediatePropagation();
                e.preventDefault();
                return true;
            }
        }, true);
    }
} catch(err) {}
</script>
""", height=0)

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .metric-title {
        color: #8b949e;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #58a6ff;
        margin-top: 4px;
    }
    .metric-subtitle {
        color: #7ee787;
        font-size: 0.82rem;
        font-weight: 500;
        margin-top: 2px;
    }
    .alert-card-warning {
        background: rgba(210, 153, 34, 0.12);
        border-left: 4px solid #d29922;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #e6edf3;
    }
    .alert-card-danger {
        background: rgba(248, 81, 73, 0.12);
        border-left: 4px solid #f85149;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #e6edf3;
    }
    .alert-card-success {
        background: rgba(46, 160, 67, 0.12);
        border-left: 4px solid #2ea043;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #e6edf3;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_engines():
    sim = SimulationEngine()
    opt = OptimizerRecommendationEngine(sim)
    return sim, opt

@st.cache_data
def get_historical_dataset():
    data_path = os.path.join(PROJECT_ROOT, "data", "Nassau_Candy_Distributor.csv")
    df, _ = load_and_preprocess(data_path)
    return df

@st.cache_data
def get_model_benchmarks():
    res_path = os.path.join(PROJECT_ROOT, "models", "model_results.csv")
    return pd.read_csv(res_path) if os.path.exists(res_path) else pd.DataFrame()

@st.cache_data
def get_cluster_data():
    return get_bottleneck_and_congested_routes()

sim_engine, opt_engine = get_engines()
raw_df = get_historical_dataset()
benchmarks_df = get_model_benchmarks()
slow_routes, congested_lanes = get_cluster_data()

with st.sidebar:
    st.markdown("## 🍬 **Decision Intelligence**")
    st.caption("Nassau Candy Logistics Optimizer")
    st.markdown("---")

    all_products = sorted(list(PRODUCT_FACTORY.keys()))
    all_regions = sorted(list(REGION_COORDS.keys()))
    all_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]

    sel_product = st.selectbox("Selected Product", all_products, index=0)
    sel_region = st.selectbox("Destination Region", all_regions, index=0)
    sel_ship_mode = st.selectbox("Ship Mode", all_modes, index=0)

    sel_units = st.slider("Units Ordered", min_value=1, max_value=50, value=2, step=1)
    prod_history = raw_df[raw_df["Product Name"] == sel_product]
    default_cost = float(prod_history["Cost"].mean()) if not prod_history.empty else 3.0
    default_sales = float(prod_history["Sales"].mean()) if not prod_history.empty else 7.5

    sel_cost = st.number_input("Manufacture Cost ($)", value=round(default_cost, 2), min_value=0.5, step=0.25)
    sel_sales = st.number_input("Gross Revenue ($)", value=round(default_sales, 2), min_value=1.0, step=0.5)

    st.markdown("---")
    st.markdown("### ⚖️ **Optimization Priority**")
    priority_slider = st.slider(
        "Priority Weight", min_value=0, max_value=100, value=50,
        help="0% = Speed (Min Lead Time) | 100% = Margin (Freight Savings)"
    )
    priority_weight = priority_slider / 100.0
    risk_tolerance = st.select_slider("Risk Tolerance", options=["Conservative", "Balanced", "Aggressive"], value="Balanced")

current_factory = PRODUCT_FACTORY.get(sel_product, "Lot's O' Nuts")
sim_df, curr_fac, curr_lt, curr_dist = sim_engine.simulate_all_factories(
    product_name=sel_product, region=sel_region, ship_mode=sel_ship_mode,
    units=sel_units, cost=sel_cost, sales=sel_sales
)
ranked_df = opt_engine.rank_factories(sim_df, priority_weight, risk_tolerance)
best_option = ranked_df.iloc[0]
best_factory = best_option["Factory"]

st.title("🍬 Nassau Candy Distributor")
st.markdown("### Factory Reallocation & Shipping Optimization Recommendation System")
st.markdown(
    "Automated decision intelligence platform predicting transit times, evaluating reallocation trade-offs, "
    "and optimizing nationwide distribution routes."
)
st.markdown("<br>", unsafe_allow_html=True)

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.markdown(f"""<div class="metric-card"><div class="metric-title">Baseline Factory</div><div class="metric-value">{current_factory}</div><div class="metric-subtitle">Default Assignment</div></div>""", unsafe_allow_html=True)
with kpi2:
    st.markdown(f"""<div class="metric-card"><div class="metric-title">Predicted Lead Time</div><div class="metric-value">{curr_lt:.0f} d</div><div class="metric-subtitle">Transit: {curr_dist:,.0f} mi</div></div>""", unsafe_allow_html=True)
with kpi3:
    st.markdown(f"""<div class="metric-card"><div class="metric-title">Recommended Hub</div><div class="metric-value">{best_factory}</div><div class="metric-subtitle">Rank #1 Candidate</div></div>""", unsafe_allow_html=True)
with kpi4:
    lt_color = "#7ee787" if best_option["Lead_Time_Delta_Days"] >= 0 else "#f85149"
    st.markdown(f"""<div class="metric-card"><div class="metric-title">Lead Time Gain</div><div class="metric-value" style="color: {lt_color};">{best_option['Lead_Time_Reduction_Pct']:+.1f}%</div><div class="metric-subtitle">{best_option['Lead_Time_Delta_Days']:+.1f} days delta</div></div>""", unsafe_allow_html=True)
with kpi5:
    st.markdown(f"""<div class="metric-card"><div class="metric-title">Reliability Score</div><div class="metric-value">{best_option['Scenario_Confidence_Score']:.1f}%</div><div class="metric-subtitle">{best_option['Risk_Classification'][:12]}</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab_sim, tab_whatif, tab_recs, tab_risk, tab_clusters, tab_geo, tab_models = st.tabs([
    "🏭 Factory Simulator", "🔄 What-If Scenario Analysis", "🏆 Recommendation Engine",
    "⚠️ Risk & Impact Panel", "🧭 Route & Lane Clustering", "🗺️ Geospatial Network Map", "🤖 Predictive ML Evaluation"
])

with tab_sim:
    st.subheader(f"Factory Performance Simulation: {sel_product}")
    st.caption(f"Simulating delivery to **{sel_region}** market via **{sel_ship_mode}** across all 5 candidate manufacturing hubs.")
    c1, c2 = st.columns([3, 2])
    with c1:
        chart_df = ranked_df.sort_values("Predicted_Lead_Time_Days")
        colors = ["#2ea043" if f == best_factory else ("#d29922" if f == current_factory else "#58a6ff") for f in chart_df["Factory"]]
        fig_lt = go.Figure(go.Bar(
            x=chart_df["Factory"], y=chart_df["Predicted_Lead_Time_Days"], marker_color=colors,
            text=[f"{v:.0f} d ({d:,.0f} mi)" for v, d in zip(chart_df["Predicted_Lead_Time_Days"], chart_df["Distance_Miles"])], textposition="auto"
        ))
        fig_lt.update_layout(paper_bgcolor="#161b22", plot_bgcolor="#161b22", font=dict(color="#e6edf3"), xaxis_title="Manufacturing Plant", yaxis_title="Lead Time (Days)", height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_lt, width="stretch")
    with c2:
        st.markdown("#### **Performance Matrix**")
        disp = ranked_df[["Rank", "Factory", "Predicted_Lead_Time_Days", "Lead_Time_Reduction_Pct", "Distance_Miles", "Est_Freight_Delta_USD", "Composite_Score"]].copy()
        disp.columns = ["Rank", "Factory", "Lead Time (d)", "Gain (%)", "Dist (mi)", "Freight Δ ($)", "Score"]
        st.dataframe(disp.set_index("Rank"), width="stretch")
        if best_factory != current_factory:
            st.markdown(f"""<div class="alert-card-success"><b>Reallocation Opportunity:</b> Transferring <b>{sel_product}</b> to <b>{best_factory}</b> shortens lead time by <b>{best_option['Lead_Time_Delta_Days']:.1f} days</b> ({best_option['Lead_Time_Reduction_Pct']:.1f}% gain) with <b>${best_option['Est_Freight_Delta_USD']:.2f}</b> estimated freight savings.</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="alert-card-warning"><b>Baseline Optimal:</b> Current assignment at <b>{current_factory}</b> holds highest score.</div>""", unsafe_allow_html=True)

with tab_whatif:
    st.subheader("What-If Scenario Sandbox")
    alt_candidates = [f for f in FACTORY_COORDS.keys() if f != current_factory]
    chosen_alt_factory = st.selectbox("Compare with Alternate Hub", alt_candidates, index=0)
    alt_row = sim_df[sim_df["Factory"] == chosen_alt_factory].iloc[0]
    col_b, col_a = st.columns(2)
    with col_b:
        st.markdown(f"""<div style="background:#161b22;border:2px solid #d29922;border-radius:12px;padding:20px;"><h4 style="color:#d29922;margin-top:0;">📍 CURRENT BASELINE</h4><h3>{current_factory}</h3><p><b>Origin:</b> {FACTORY_DETAILS[current_factory]['city']}, {FACTORY_DETAILS[current_factory]['state']}</p><hr style="border-color:#30363d;"><p><b>Lead Time:</b> {curr_lt:.1f} Days</p><p><b>Distance:</b> {curr_dist:,.0f} Miles</p><p><b>Est. Freight:</b> ${curr_dist * sel_units * BASE_FREIGHT_COST_PER_MILE_UNIT:.2f}</p></div>""", unsafe_allow_html=True)
    with col_a:
        delta_lt = curr_lt - alt_row["Predicted_Lead_Time_Days"]
        border_col = "#2ea043" if delta_lt >= 0 else "#f85149"
        st.markdown(f"""<div style="background:#161b22;border:2px solid {border_col};border-radius:12px;padding:20px;"><h4 style="color:{border_col};margin-top:0;">🔄 SIMULATED ALTERNATIVE</h4><h3>{chosen_alt_factory}</h3><p><b>Origin:</b> {FACTORY_DETAILS[chosen_alt_factory]['city']}, {FACTORY_DETAILS[chosen_alt_factory]['state']}</p><hr style="border-color:#30363d;"><p><b>Lead Time:</b> {alt_row['Predicted_Lead_Time_Days']:.1f} Days ({alt_row['Lead_Time_Reduction_Pct']:+.1f}%)</p><p><b>Distance:</b> {alt_row['Distance_Miles']:,.0f} Miles ({alt_row['Distance_Delta_Miles']:+.0f} mi)</p><p><b>Freight Δ:</b> {alt_row['Est_Freight_Delta_USD']:+.2f} USD</p></div>""", unsafe_allow_html=True)

with tab_recs:
    st.subheader("Enterprise Reassignment Recommendations")
    top_n_slider = st.slider("Display Count", min_value=3, max_value=25, value=10)
    top_recs, all_recs, coverage_pct = opt_engine.generate_global_recommendations(priority_weight=priority_weight, risk_tolerance=risk_tolerance, top_n=top_n_slider)
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Recommendation Coverage", f"{coverage_pct:.1f}%")
    r2.metric("Avg Days Saved", f"{top_recs['Days_Saved'].mean():.1f} days" if not top_recs.empty else "0.0")
    r3.metric("Avg Freight Savings", f"${top_recs['Est_Freight_Savings_USD'].mean():.2f}" if not top_recs.empty else "$0.00")
    r4.metric("Avg Confidence", f"{top_recs['Confidence_Score'].mean():.1f}%" if not top_recs.empty else "0.0%")
    if not top_recs.empty:
        st.dataframe(top_recs[["Product", "Destination_Region", "Current_Factory", "Recommended_Factory", "Days_Saved", "Lead_Time_Reduction_Pct", "Miles_Saved", "Est_Freight_Savings_USD", "Confidence_Score", "Risk_Level"]], width="stretch")
        st.download_button("📥 Download Recommendations CSV", top_recs.to_csv(index=False).encode('utf-8'), "recommendations.csv", "text/csv")

with tab_risk:
    st.subheader("Risk & Operational Impact Assessment")
    c_rl, c_rr = st.columns(2)
    with c_rl:
        st.markdown("#### 🚨 **Identified Reassignment Warnings**")
        high_risks = ranked_df[ranked_df["Risk_Classification"].str.contains("HIGH|MODERATE")]
        if not high_risks.empty:
            for _, r in high_risks.iterrows():
                st.markdown(f"""<div class="alert-card-danger"><b>{r['Factory']}:</b> {r['Risk_Classification']}<br><small>Lead time delta: {r['Lead_Time_Delta_Days']:+.1f} d | Dist delta: {r['Distance_Delta_Miles']:+.0f} mi</small></div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="alert-card-success"><b>Zero High-Risk Anomalies:</b> Candidate reassignments operate within tolerance.</div>""", unsafe_allow_html=True)
    with c_rr:
        st.markdown("#### 🏭 **Plant Capacity & Load**")
        fac_loads = []
        for fac_name, meta in FACTORY_DETAILS.items():
            curr_products = [p for p, f in PRODUCT_FACTORY.items() if f == fac_name]
            unit_volume = raw_df[raw_df["Product Name"].isin(curr_products)]["Units"].sum()
            utilization = (unit_volume / meta["capacity_units_yr"]) * 100.0
            fac_loads.append({"Factory": fac_name, "Capacity": meta["capacity_units_yr"], "Current Volume": unit_volume, "Utilization %": round(utilization, 1)})
        st.dataframe(pd.DataFrame(fac_loads).set_index("Factory"), width="stretch")

with tab_clusters:
    st.subheader("Route & Product Clustering Analysis")
    cl1, cl2 = st.columns(2)
    with cl1:
        st.markdown("#### 🐢 **Slow Routes (Severe Bottlenecks)**")
        st.dataframe(slow_routes[["Factory", "Region", "Product Name", "Ship Mode", "Avg_Lead_Time", "Avg_Distance", "Order_Count"]].head(12), width="stretch")
    with cl2:
        st.markdown("#### 🚦 **Congested High-Volume Lanes**")
        st.dataframe(congested_lanes[["Factory", "Region", "Product Name", "Total_Units", "Total_Sales", "Avg_Profit_Margin"]].head(12), width="stretch")

with tab_geo:
    st.subheader("Interactive Nationwide Logistics Map")
    map_fig = build_geospatial_network_map(selected_factory=best_factory, selected_region=sel_region)
    st.plotly_chart(map_fig, width="stretch")

with tab_models:
    st.subheader("Machine Learning Model Benchmarking")
    if not benchmarks_df.empty:
        st.dataframe(benchmarks_df.set_index("Model"), width="stretch")
