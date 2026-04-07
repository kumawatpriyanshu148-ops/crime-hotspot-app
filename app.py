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

# 🚓 multiple police stations
police_stations = {
    "Jaipur": [
        (26.923, 75.800, "Vaishali Nagar Police Station"),
        (26.905, 75.775, "Mansarovar Police Station"),
        (26.930, 75.820, "Vidyadhar Nagar Police Station")
    ],
    "Delhi": [
        (28.620, 77.220, "Connaught Place Police Station"),
        (28.600, 77.190, "Karol Bagh Police Station"),
        (28.640, 77.230, "Civil Lines Police Station")
    ],
    "Mumbai": [
        (19.080, 72.880, "Andheri Police Station"),
        (19.060, 72.860, "Bandra Police Station"),
        (19.100, 72.900, "Powai Police Station")
    ]
}

# ---------------- FILTER ----------------
filtered_df = df[df["Crime_Type"] == crime_type].copy()
if filtered_df.empty:
    filtered_df = df.copy()

# ---------------- CONTROLS ----------------
st.subheader("🎛️ Prediction Controls")
hour = st.slider("Hour", 0, 23, 0)
temp = st.slider("Temperature (°C)", 10, 50, 25)
pop = st.slider("Population Density", 100, 1000, 500)

# ---------------- DYNAMIC CITY SHIFT ----------------
center = city_coords[city]
spread = temp / 1200

seed_val = hour + temp + pop + abs(hash(city)) % 1000
np.random.seed(seed_val)

num_dots = min(150, len(filtered_df))
final_df = filtered_df.sample(num_dots, random_state=seed_val).copy()

final_df["Latitude"] = center[0] + np.random.normal(0, 0.05, num_dots)
final_df["Longitude"] = center[1] + np.random.normal(0, 0.05, num_dots)

# ---------------- TIME-BASED RISK RATIO ----------------
# hour=0 => G75 Y20 R5
# hour=23 => R75 Y15 G10
red_ratio = 0.05 + (hour / 23) * 0.70
yellow_ratio = 0.20 - (hour / 23) * 0.05
green_ratio = 1 - red_ratio - yellow_ratio

num_red = int(num_dots * red_ratio)
num_yellow = int(num_dots * yellow_ratio)
num_green = num_dots - num_red - num_yellow

colors = (
    ["red"] * num_red +
    ["yellow"] * num_yellow +
    ["green"] * num_green
)

np.random.shuffle(colors)

# ---------------- MAP ----------------
st.subheader("🗺️ Crime Hotspots Map")
crime_map = folium.Map(location=center, zoom_start=12)

for idx, row in final_df.reset_index(drop=True).iterrows():
    lat = float(row["Latitude"])
    lon = float(row["Longitude"])
    color = colors[idx]

    folium.CircleMarker(
        location=[lat, lon],
        radius=max(5, pop / 220),
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=1.0,
        weight=2,
        popup=f"{color.upper()} Risk"
    ).add_to(crime_map)

# 🚓 police stations
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

# ---------------- STATS ----------------
st.subheader("📊 Risk Distribution")
col1, col2, col3 = st.columns(3)

col1.metric("🟢 Low Risk", f"{green_ratio*100:.0f}%")
col2.metric("🟡 Medium Risk", f"{yellow_ratio*100:.0f}%")
col3.metric("🔴 High Risk", f"{red_ratio*100:.0f}%")
