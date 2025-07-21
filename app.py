import streamlit as st
import streamlit.components.v1 as components
import math, json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

st.set_page_config(layout="wide",
                   page_title="Polar Orbit Simulator",
                   page_icon="🛸️")

def main():
    # ---------- Title ----------
    st.markdown(
        """
        <style>.main-title{font-size:2.5em;font-weight:bold;margin-bottom:0.2em}.subtitle{color:#555}</style>
        <div class='main-title'>🛸️ Polar Orbit Simulator</div>
        <div class='subtitle'>Design and visualize satellite constellations in Low‑Earth Orbit.</div>
        """, unsafe_allow_html=True)

    # ---------- Sidebar ----------
    with st.sidebar:
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/4/4f/Satellite_icon.svg",
            width=100
        )
        st.header("Configure Orbit")

        mission_type = st.selectbox(
            "Mission Type",
            ["High-Resolution Imaging", "Weather Observation", "Communications"]
        )
        max_angle_deg, alt_min, alt_max, alt_default = (
            (5, 450, 600, 500) if mission_type == "High-Resolution Imaging" else
            (25, 600, 900, 800) if mission_type == "Weather Observation" else
            (45, 700, 1200, 1000)
        )

        altitude_km = st.slider("Altitude (km)", alt_min, alt_max, alt_default, step=50)
        inclination = st.number_input("Inclination (°)", min_value=0, max_value=180, value=90)
        num_sats = st.slider("Satellites", min_value=1, max_value=5, value=3)
        sim_hours = st.slider("Simulation Duration (hrs)", min_value=1, max_value=24, value=24)

        st.markdown("### Satellite Visibility")
        selected_sats = [i - 1 for i in range(1, num_sats + 1)
                         if st.checkbox(f"SAT-{i}", True, key=f"sat_{i}")]

        with st.expander("Display Options"):
            show_tracks = st.checkbox("Show Ground Track", True)
            show_swath = st.checkbox("Show Coverage Swath", True)
            orbit_color = st.color_picker("Orbit Color", "#FF0000")
            show_labels = st.checkbox("Show Base Labels", True)

        base_df = pd.read_csv("us_bases_large.csv")
        branch_colors = {
            "Army": "green", "Navy": "blue", "Air Force": "red",
            "Space Force": "purple", "Marine": "orange",
            "Joint": "gray", "Command": "gold", "Research": "cyan",
            "Other": "white"
        }
        base_df["Color"] = base_df["Branch"].map(branch_colors).fillna("white")

        with st.expander("Base Filters"):
            st.markdown("##### Branch")
            sel_branches = [
                br for br in sorted(base_df["Branch"].unique())
                if st.checkbox(br, True, key=f"br_{br}")
            ]
            st.markdown("##### Region")
            sel_regions = [
                rg for rg in sorted(base_df["Region"].dropna().unique())
                if st.checkbox(rg, True, key=f"rg_{rg}")
            ] if "Region" in base_df.columns else []

        if sel_branches:
            base_df = base_df[base_df["Branch"].isin(sel_branches)]
        if sel_regions:
            base_df = base_df[base_df["Region"].isin(sel_regions)]

    # ---------- Configuration Metrics ----------
    st.subheader("Current Configuration")
    c1, c2, c3 = st.columns(3)
    c1.metric("Altitude", f"{altitude_km} km")
    c2.metric("Inclination", f"{inclination}°")
    c3.metric("Satellites", num_sats)

    # ---------- Orbit & Analytics ----------
    with st.spinner("Simulating orbits..."):
        ground_radius_km = (6371 + altitude_km) * math.tan(math.radians(max_angle_deg))
        orbit_tracks = []
        now = datetime.utcnow()
        duration = int(sim_hours * 3600)

        base_pass_counts = {name: 0 for name in base_df["Name"]}
        base_cover_times = {name: [] for name in base_df["Name"]}

        base_coords_rad = np.radians(base_df[['Latitude', 'Longitude']].values)
        base_names = base_df['Name'].values

        for s in range(num_sats):
            track = []
            for t in range(0, duration, 600):  # sample every 10 min
                ts = now + timedelta(seconds=t)
                mean = (360 * t / 5400) % 360
                lon_off = (360 * t / 86400) % 360
                theta = math.radians(mean + (360 / num_sats) * s)
                lat = math.degrees(
                    math.asin(math.sin(math.radians(inclination)) * math.sin(theta))
                )
                lon = (mean + (360 / num_sats) * s - lon_off) % 360
                track.append({"time": ts.isoformat(), "pos": [lon, lat, altitude_km * 1000]})

                # Vectorized haversine distance
                phi1 = np.radians(lat)
                phi2 = base_coords_rad[:, 0]
                dphi = phi2 - phi1
                dlmb = base_coords_rad[:, 1] - np.radians(lon)

                a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlmb / 2) ** 2
                c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
                distances = 6371 * c

                covered_indices = np.where(distances <= ground_radius_km)[0]
                for idx in covered_indices:
                    name = base_names[idx]
                    base_pass_counts[name] += 1
                    base_cover_times[name].append(ts)

            orbit_tracks.append(track)

    # ---------- Compute Analytics ----------
    unique_positions = {
        (round(p["pos"][0], 2), round(p["pos"][1], 2))
        for sat in orbit_tracks for p in sat
    }
    redundancy_index = len(orbit_tracks) / len(unique_positions) if unique_positions else 0

    global_max_gap = 0
    for times in base_cover_times.values():
        if times:
            sorted_times = sorted(times)
            gaps = [
                (t2 - t1).total_seconds()
                for t1, t2 in zip(sorted_times, sorted_times[1:])
            ]
            gaps.append((sorted_times[0] - now).total_seconds())
            gaps.append((now + timedelta(seconds=duration) - sorted_times[-1]).total_seconds())
            global_max_gap = max(global_max_gap, max(gaps))
    longest_gap_min = global_max_gap / 60

    st.subheader("Mission Analytics")
    a1, a2 = st.columns(2)
    a1.metric("Redundancy Index", f"{redundancy_index:.2f}")
    a2.metric("Longest Coverage Gap", f"{longest_gap_min:.1f} min")

    if redundancy_index > 1.5:
        st.warning("High redundancy: consider reducing satellites or lowering altitude.")
    elif redundancy_index < 1:
        st.error("Low redundancy: add satellites or increase altitude to fill gaps.")
    else:
        st.success("Redundancy is balanced.")

    st.subheader("Pass Count per Base")
    df_pass = pd.DataFrame({
        "Base": list(base_pass_counts.keys()),
        "Pass Count": list(base_pass_counts.values())
    })
    st.dataframe(df_pass)

    # ---------- Render Cesium ----------
    orbit_json = json.dumps(orbit_tracks)
    base_json = base_df.to_json(orient="records")

    html = f"""
<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<script src='https://cesium.com/downloads/cesiumjs/releases/1.104/Build/Cesium/Cesium.js'></script>
<link rel='stylesheet' href='https://cesium.com/downloads/cesiumjs/releases/1.104/Build/Cesium/Widgets/widgets.css'>
<style>html,body,#cesiumContainer{{width:100%;height:100%;margin:0;overflow:hidden}}</style>
</head><body><div id='cesiumContainer'></div>
<script>
Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI0M2FiNWM0MC1iMmE2LTRlZDQtOGZkYi1lYmU5MWMwZDgzZWUiLCJpZCI6MzE3MTk5LCJpYXQiOjE3NTEzMTM4NTF9.ACpugJD39iub0RRbaFzm2Khn38bqyjednnRyAr-QRag';
const viewer = new Cesium.Viewer('cesiumContainer', {{
  terrainProvider: Cesium.createWorldTerrain(),
  timeline: true,
  animation: true
}});
const tracks = {orbit_json};
const baseData = {base_json};
const orbitCol = Cesium.Color.fromCssColorString('{orbit_color}');

tracks.forEach((sat, idx) => {{
  const prop = new Cesium.SampledPositionProperty();
  const pts = [];
  sat.forEach(p => {{
    prop.addSample(
      Cesium.JulianDate.fromIso8601(p.time),
      Cesium.Cartesian3.fromDegrees(...p.pos)
    );
    pts.push(p.pos[0], p.pos[1]);
  }});
  viewer.entities.add({{
    position: prop,
    point: {{ pixelSize: 6, color: orbitCol }},
    path: {{ width: 2, material: orbitCol }}
  }});
  if ({str(show_tracks).lower()}) {{
    viewer.entities.add({{
      polyline: {{
        positions: Cesium.Cartesian3.fromDegreesArray(pts),
        width: 1,
        material: Cesium.Color.YELLOW.withAlpha(0.4)
      }}
    }});
  }}
}});

baseData.forEach(b => {{
  viewer.entities.add({{
    position: Cesium.Cartesian3.fromDegrees(b.Longitude, b.Latitude),
    point: {{ pixelSize: 8, color: Cesium.Color.fromCssColorString(b.Color) }},
    label: {str(show_labels).lower()} ? {{
      text: b.Name,
      font: '10px sans-serif',
      fillColor: Cesium.Color.WHITE,
      outlineColor: Cesium.Color.BLACK,
      outlineWidth: 1
    }} : undefined
  }});
}});
</script>
</body></html>
"""
    components.html(html, height=700)

if __name__ == '__main__':
    main()




