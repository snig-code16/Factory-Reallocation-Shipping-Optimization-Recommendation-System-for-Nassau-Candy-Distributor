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
        textposition="top center", textfont=dict(color="#0f172a", size=10),
        marker=dict(size=14, color=["#d97706" if f == selected_factory else "#2563eb" for f in f_names], symbol="diamond", line=dict(width=2, color="#ffffff")), hoverinfo="text"
    ))

    r_lats, r_lons, r_names, r_texts = [], [], [], []
    for r_name, (lat, lon) in REGION_COORDS.items():
        r_lats.append(lat)
        r_lons.append(lon)
        r_names.append(r_name)
        r_texts.append(f"<b>Demand Region: {r_name}</b>")

    fig.add_trace(go.Scattergeo(
        lon=r_lons, lat=r_lats, text=r_texts, mode="markers+text", name="Regional Markets",
        textposition="bottom center", textfont=dict(color="#0f172a", size=10),
        marker=dict(size=11, color=["#dc2626" if r == selected_region else "#7c3aed" for r in r_names], symbol="circle", line=dict(width=1.5, color="#ffffff")), hoverinfo="text"
    ))

    if selected_factory and selected_region and selected_factory in FACTORY_COORDS and selected_region in REGION_COORDS:
        f_coord = FACTORY_COORDS[selected_factory]
        r_coord = REGION_COORDS[selected_region]
        fig.add_trace(go.Scattergeo(
            lon=[f_coord[1], r_coord[1]], lat=[f_coord[0], r_coord[0]], mode="lines",
            line=dict(width=3, color="#16a34a", dash="dash"), name="Simulated Lane", hoverinfo="none"
        ))

    fig.update_layout(
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            showland=True,
            landcolor="#f8fafc",
            subunitcolor="#cbd5e1",
            countrycolor="#94a3b8",
            showlakes=True,
            lakecolor="#e0f2fe",
            bgcolor="#ffffff"
        ),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#1e293b"),
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(x=0.02, y=0.98, bgcolor="rgba(255, 255, 255, 0.95)", bordercolor="#cbd5e1", borderwidth=1, font=dict(color="#1e293b")),
        height=450
    )
    return fig
