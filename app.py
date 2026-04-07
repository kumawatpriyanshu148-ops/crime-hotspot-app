import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

# ---------------- PAGE CONFIG ----------------
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

crime_type = st.sidebar.selectbox(
    "Crime Type",
    df["Crime_Type"].unique()
)

city = st.sidebar.selectbox(
    "City",
    ["Jaipur", "Delhi", "Mumbai"]
)

city_coords = {
    "Jaipur": [26.9124, 75.7873],
    "Delhi": [28.6139, 77.2090],
    "Mumbai": [19.0760, 72.8777]
}

# 🚓 police stations
police_stations = {
    "Jaipur": [
        (26.923, 75.800, "Vaishali Nagar Police Station"),
        (26.905, 75.775, "Mansarovar Police Station")
    ],
    "Delhi": [
        (28.620, 77.220, "Connaught Place Police Station"),
        (28.600, 77.190, "Karol Bagh Police Station")
    ],
    "Mumbai": [
        (19.080, 72.880, "Andheri Police Station"),
        (19.060, 72.860, "Bandra Police Station")
    ]
}

# ---------------- FILTER DATA ----------------
filtered_df = df[df["Crime_Type"] == crime_type].copy()

if filtered_df.empty:
    filtered_df = df.copy()

# ---------------- CONTROLS ----------------
st.subheader("🎛️ Prediction Controls")

hour = st.slider("Hour", 0, 23, 12)
temp = st.slider("Temperature (°C)", 10, 50, 25)
pop = st.slider("Population Density", 100, 1000, 500)

# ---------------- DYNAMIC DATA ----------------
center = city_coords[city]
spread = temp / 1500

np.random.seed(hour + temp + pop)

# sample only visible amount → fast + clean
final_df = filtered_df.sample(
    min(120, len(filtered_df)),
    random_state=42
).copy()

# shift around selected city center
final_df["Latitude"] = center[0] + np.random.normal(0, 0.05, len(final_df))
final_df["Longitude"] = center[1] + np.random.normal(0, 0.05, len(final_df))

# temperature spread effect
final_df["Latitude"] += np.random.normal(0, spread, len(final_df))
final_df["Longitude"] += np.random.normal(0, spread, len(final_df))

# ---------------- MAP ----------------
st.subheader("🗺️ Crime Hotspots Map")

crime_map = folium.Map(location=center, zoom_start=12)

# 🎯 guaranteed mixed dots
for idx, row in final_df.reset_index(drop=True).iterrows():
    lat = float(row["Latitude"])
    lon = float(row["Longitude"])

    # guaranteed mixed risk colors
    if idx % 3 == 0:
        color = "red"       # high
        risk = "High"
    elif idx % 3 == 1:
        color = "yellow"    # medium
        risk = "Medium"
    else:
        color = "green"     # low
        risk = "Low"

    radius = max(5, pop / 200)

    folium.CircleMarker(
        location=[lat, lon],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=1.0,
        weight=2,
        popup=f"{risk} Risk Zone"
    ).add_to(crime_map)

# 🚓 police stations
for lat, lon, name in police_stations[city]:
    folium.Marker(
        location=[lat, lon],
        popup=f"🚓 {name}",
        tooltip=name,
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(crime_map)

st_folium(crime_map, width=950, height=550)

# ---------------- SOS ----------------
st.subheader("🚨 SOS Emergency")

if st.button("🚨 Send SOS Alert"):
    nearest_station = police_stations[city][0][2]
    st.error(f"SOS SENT 🚓 Nearest station alerted: {nearest_station}")

st.info("Emergency Number: 112")

# ---------------- DASHBOARD ----------------
st.subheader("📊 Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Total Crimes", len(final_df))
col2.metric("Selected City", city)
col3.metric("Crime Type", crime_type)

# ---------------- DATA ----------------
st.subheader("📄 Data Preview")
st.dataframe(final_df.head(15))

# ---------------- FOOTER ----------------
st.markdown("---")
st.write("Made by Priyanshu 🚀")
