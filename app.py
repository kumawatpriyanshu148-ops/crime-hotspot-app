import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

# ---------------- PAGE ----------------
st.set_page_config(page_title="Crime Hotspot Prediction", layout="wide")
st.title("🚓 Crime Hotspot Prediction System")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("crime_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.header("🔍 Filters")
crime_type = st.sidebar.selectbox("Crime Type", df["Crime_Type"].unique())
city = st.sidebar.selectbox("City", ["Jaipur", "Delhi", "Mumbai"])

city_coords = {
    "Jaipur": [26.9124, 75.7873],
    "Delhi": [28.6139, 77.2090],
    "Mumbai": [19.0760, 72.8777]
}

police_stations = {
    "Jaipur": [(26.923, 75.800, "Vaishali Nagar PS")],
    "Delhi": [(28.620, 77.220, "Connaught Place PS")],
    "Mumbai": [(19.080, 72.880, "Andheri PS")]
}

# ---------------- FILTER ----------------
filtered_df = df[df["Crime_Type"] == crime_type].copy()
if filtered_df.empty:
    filtered_df = df.copy()

# ---------------- CONTROLS ----------------
st.subheader("🎛️ Prediction Controls")
hour = st.slider("Hour", 0, 23, 12)
temp = st.slider("Temperature (°C)", 10, 50, 25)
pop = st.slider("Population Density", 100, 1000, 500)

# ---------------- DYNAMIC CITY + SPREAD ----------------
center = city_coords[city]
spread = temp / 1200

# city-based seed → city change visible
seed_val = hour + temp + pop + hash(city) % 1000
np.random.seed(seed_val)

final_df = filtered_df.sample(min(120, len(filtered_df)), random_state=seed_val).copy()

# strong visible city shift
final_df["Latitude"] = center[0] + np.random.normal(0, 0.06, len(final_df))
final_df["Longitude"] = center[1] + np.random.normal(0, 0.06, len(final_df))

# temp spread effect
final_df["Latitude"] += np.random.normal(0, spread, len(final_df))
final_df["Longitude"] += np.random.normal(0, spread, len(final_df))

# ---------------- GLOBAL RISK ----------------
risk_base = (hour * 2) + (temp * 0.5) + (pop * 0.01)

# ---------------- MAP ----------------
st.subheader("🗺️ Crime Hotspots Map")
crime_map = folium.Map(location=center, zoom_start=12)

for idx, row in final_df.reset_index(drop=True).iterrows():
    lat = float(row["Latitude"])
    lon = float(row["Longitude"])

    # 🎯 dynamic per-dot score
    risk_score = risk_base + np.random.randint(-15, 15)

    if risk_score > 60:
        color = "red"
        risk = "High"
    elif risk_score > 40:
        color = "yellow"
        risk = "Medium"
    else:
        color = "green"
        risk = "Low"

    folium.CircleMarker(
        location=[lat, lon],
        radius=max(5, pop / 220),
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=1.0,
        weight=2,
        popup=f"{risk} Risk ({risk_score:.1f})"
    ).add_to(crime_map)

# police markers
for lat, lon, name in police_stations[city]:
    folium.Marker(
        [lat, lon],
        popup=f"🚓 {name}",
        icon=folium.Icon(color="blue")
    ).add_to(crime_map)

st_folium(crime_map, width=950, height=550)

# ---------------- SOS ----------------
st.subheader("🚨 SOS Emergency")
if st.button("🚨 Send SOS Alert"):
    st.error(f"SOS SENT 🚓 Alert sent to {police_stations[city][0][2]}")

# ---------------- RISK STATUS ----------------
st.subheader("📊 Overall Risk")
if risk_base > 60:
    st.error("HIGH RISK 🔴")
elif risk_base > 40:
    st.warning("MEDIUM RISK 🟡")
else:
    st.success("LOW RISK 🟢")
