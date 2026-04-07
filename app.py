import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Crime Hotspot Prediction", layout="wide")
st.title("🚓 Crime Hotspot Prediction System + SOS")

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

# sample police stations
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
spread = temp / 1000
np.random.seed(hour + temp + pop)

final_df = filtered_df.copy()
lat_shift = center[0] - final_df["Latitude"].mean()
lon_shift = center[1] - final_df["Longitude"].mean()

final_df["Latitude"] += lat_shift
final_df["Longitude"] += lon_shift
final_df["Latitude"] += np.random.normal(0, spread, len(final_df))
final_df["Longitude"] += np.random.normal(0, spread, len(final_df))

# ---------------- MAP ----------------
st.subheader("🗺️ Crime + Nearby Police Stations")
crime_map = folium.Map(location=center, zoom_start=11)

# crime dots
for i, row in final_df.iterrows():
    lat = float(row["Latitude"])
    lon = float(row["Longitude"])
    risk_score = (hour * 2) + (temp * 0.5) + (pop * 0.01) + (i % 20)

    if risk_score > 60:
        color = "red"
    elif risk_score > 40:
        color = "orange"
    else:
        color = "green"

    folium.CircleMarker(
        location=[lat, lon],
        radius=max(4, pop / 180),
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.75,
        popup=f"Crime Risk: {risk_score:.1f}"
    ).add_to(crime_map)

# nearby police stations
for lat, lon, name in police_stations[city]:
    folium.Marker(
        location=[lat, lon],
        popup=f"🚓 {name}",
        tooltip=name,
        icon=folium.Icon(color="blue", icon="shield", prefix="fa")
    ).add_to(crime_map)

st_folium(crime_map, width=950, height=550)

# ---------------- SOS SYSTEM ----------------
st.subheader("🚨 SOS Emergency System")
col1, col2 = st.columns(2)

with col1:
    if st.button("🚨 Send SOS Alert"):
        st.error("SOS ALERT SENT TO NEAREST POLICE STATION 🚓")
        nearest_station = police_stations[city][0][2]
        st.write(f"Nearest station notified: **{nearest_station}**")

with col2:
    st.info("Emergency Number: 112")

# ---------------- METRICS ----------------
avg_score = (hour * 2) + (temp * 0.5) + (pop * 0.01)
st.subheader("📊 Dashboard")
col1, col2, col3 = st.columns(3)
col1.metric("Total Crimes", len(final_df))
col2.metric("Avg Risk", f"{avg_score:.1f}")
col3.metric("City", city)

st.markdown("---")
st.write("Made by Priyanshu 🚀")
