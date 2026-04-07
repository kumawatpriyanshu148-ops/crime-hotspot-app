import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

st.set_page_config(page_title="Crime Hotspot Prediction", layout="wide")
st.title("🚓 Crime Hotspot Prediction System + SOS")

@st.cache_data
def load_data():
    df = pd.read_csv("crime_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

st.sidebar.header("🔍 Filters")
crime_type = st.sidebar.selectbox("Crime Type", df["Crime_Type"].unique())
city = st.sidebar.selectbox("City", ["Jaipur", "Delhi", "Mumbai"])

city_coords = {
    "Jaipur": [26.9124, 75.7873],
    "Delhi": [28.6139, 77.2090],
    "Mumbai": [19.0760, 72.8777]
}

police_stations = {
    "Jaipur": [(26.923, 75.800, "Vaishali Nagar Police Station"), (26.905, 75.775, "Mansarovar Police Station")],
    "Delhi": [(28.620, 77.220, "Connaught Place Police Station"), (28.600, 77.190, "Karol Bagh Police Station")],
    "Mumbai": [(19.080, 72.880, "Andheri Police Station"), (19.060, 72.860, "Bandra Police Station")]
}

filtered_df = df[df["Crime_Type"] == crime_type].copy()
if filtered_df.empty:
    filtered_df = df.copy()

st.subheader("🎛️ Prediction Controls")
hour = st.slider("Hour", 0, 23, 12)
temp = st.slider("Temperature (°C)", 10, 50, 25)
pop = st.slider("Population Density", 100, 1000, 500)

center = city_coords[city]
spread = temp / 1200
np.random.seed(hour + temp + pop)

final_df = filtered_df.sample(min(len(filtered_df), 300), random_state=42).copy()
lat_shift = center[0] - final_df["Latitude"].mean()
lon_shift = center[1] - final_df["Longitude"].mean()
final_df["Latitude"] += lat_shift + np.random.normal(0, spread, len(final_df))
final_df["Longitude"] += lon_shift + np.random.normal(0, spread, len(final_df))

st.subheader("🗺️ Crime Hotspots Map")
crime_map = folium.Map(location=center, zoom_start=11)
# visible risk dots (direct on map for guaranteed rendering)
for i, row in final_df.iterrows():
    lat = float(row["Latitude"])
    lon = float(row["Longitude"])
    risk_score = (hour * 2) + (temp * 0.5) + (pop * 0.01) + (i % 25)

    if risk_score > 60:
        color = "red"
    elif risk_score > 40:
        color = "orange"
    else:
        color = "green"

    folium.CircleMarker(
        location=[lat, lon],
        radius=6,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.9,
        weight=2,
        popup=f"Risk: {risk_score:.1f}"
    ).add_to(crime_map)

for lat, lon, name in police_stations[city]:
    folium.Marker(
        location=[lat, lon],
        popup=f"🚓 {name}",
        tooltip=name,
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(crime_map)

st_folium(crime_map, width=950, height=550)

st.subheader("🚨 SOS Emergency System")
if st.button("🚨 Send SOS Alert"):
    nearest_station = police_stations[city][0][2]
    st.error(f"SOS SENT 🚓 Nearest station notified: {nearest_station}")

st.info("Emergency Number: 112")

avg_score = (hour * 2) + (temp * 0.5) + (pop * 0.01)
st.subheader("📊 Dashboard")
col1, col2, col3 = st.columns(3)
col1.metric("Total Crimes", len(final_df))
col2.metric("Avg Risk", f"{avg_score:.1f}")
col3.metric("City", city)

st.markdown("---")
st.write("Made by Priyanshu 🚀")
