import plotly.graph_objects as go
from src.config import FACTORY_COORDS, FACTORY_DETAILS, REGION_COORDS

def build_geospatial_network_map(selected_factory=None, selected_region=None):
    fig = go.Figure()
    f_lats, f_lons, f_names, f_texts = [], [], [], []
    for f_name, (lat, lon) in FACTORY_COORDS.items():
        f_lats.append(lat)
        f_lons.append(lon)
        f_names.append(f_name)
        detail = FACTORY_DETAILS[f_name]
        f_texts.append(f"<b>Factory: {f_name}</b><br>{detail['city']}, {detail['state']}<br>Capacity: {detail['capacity_units_yr']:,} units/yr")

    fig.add_trace(go.Scattergeo(
        lon=f_lons, lat=f_lats, text=f_texts, mode="markers+text", name="Manufacturing Hubs",
        textposition="top center", marker=dict(size=14, color=["#ffbe0b" if f == selected_factory else "#3a86ff" for f in f_names], symbol="diamond", line=dict(width=2, color="#ffffff")), hoverinfo="text"
    ))

    r_lats, r_lons, r_names, r_texts = [], [], [], []
    for r_name, (lat, lon) in REGION_COORDS.items():
        r_lats.append(lat)
        r_lons.append(lon)
        r_names.append(r_name)
        r_texts.append(f"<b>Demand Region: {r_name}</b>")

    fig.add_trace(go.Scattergeo(
        lon=r_lons, lat=r_lats, text=r_texts, mode="markers+text", name="Regional Markets",
        textposition="bottom center", marker=dict(size=11, color=["#ff006e" if r == selected_region else "#8338ec" for r in r_names], symbol="circle", line=dict(width=1.5, color="#ffffff")), hoverinfo="text"
    ))

    if selected_factory and selected_region and selected_factory in FACTORY_COORDS and selected_region in REGION_COORDS:
        f_coord = FACTORY_COORDS[selected_factory]
        r_coord = REGION_COORDS[selected_region]
        fig.add_trace(go.Scattergeo(
            lon=[f_coord[1], r_coord[1]], lat=[f_coord[0], r_coord[0]], mode="lines",
            line=dict(width=3, color="#06d6a0", dash="dash"), name="Simulated Lane", hoverinfo="none"
        ))

    fig.update_layout(
        geo=dict(scope="usa", projection_type="albers usa", showland=True, landcolor="#181a20", subunitcolor="#343a40", countrycolor="#495057", showlakes=True, lakecolor="#101216", bgcolor="#0e1117"),
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117", font=dict(color="#f8f9fa"), margin=dict(l=0, r=0, t=20, b=0), legend=dict(x=0.02, y=0.98, bgcolor="rgba(14, 17, 23, 0.7)"), height=450
    )
    return fig
