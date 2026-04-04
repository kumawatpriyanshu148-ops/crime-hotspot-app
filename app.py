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

# ---------------- SIDEBAR FILTERS ----------------
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

# ---------------- FILTER DATA ----------------
filtered_df = df[df["Crime_Type"] == crime_type].copy()

if filtered_df.empty:
    filtered_df = df.copy()

# ---------------- CONTROLS ----------------
st.subheader("🎛️ Prediction Controls")

hour = st.slider("Hour", 0, 23, 12)
temp = st.slider("Temperature (°C)", 10, 50, 25)
pop = st.slider("Population Density", 100, 1000, 500)

# ---------------- DYNAMIC EFFECT ----------------
spread = temp / 1000
np.random.seed(hour + temp + pop)

final_df = filtered_df.copy()

# city center shift
center = city_coords[city]
lat_shift = center[0] - final_df["Latitude"].mean()
lon_shift = center[1] - final_df["Longitude"].mean()

final_df["Latitude"] += lat_shift
final_df["Longitude"] += lon_shift

# temperature spread effect
final_df["Latitude"] += np.random.normal(0, spread, len(final_df))
final_df["Longitude"] += np.random.normal(0, spread, len(final_df))

# ---------------- MAP ----------------
st.subheader("🗺️ Crime Hotspots Map")

crime_map = folium.Map(location=center, zoom_start=11)

for i, row in final_df.iterrows():
    lat = float(row["Latitude"])
    lon = float(row["Longitude"])

    # 🎯 Per-dot risk score
    risk_score = (hour * 2) + (temp * 0.5) + (pop * 0.01) + (i % 20)

    if risk_score > 60:
        color = "red"       # high risk
    elif risk_score > 40:
        color = "yellow"    # medium risk
    else:
        color = "green"     # low risk

    # population → size effect
    radius = max(4, pop / 180)

    folium.CircleMarker(
        location=[lat, lon],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.75,
        popup=f"""
        Crime: {crime_type}
        <br>Risk Score: {risk_score:.1f}
        <br>Hour: {hour}
        <br>Temp: {temp}°C
        <br>Population: {pop}
        """
    ).add_to(crime_map)

st_folium(crime_map, width=950, height=550)

# ---------------- GLOBAL RISK ----------------
avg_score = (hour * 2) + (temp * 0.5) + (pop * 0.01)

st.subheader("🚨 Overall Risk Level")

if avg_score > 60:
    st.error("HIGH RISK 🔴")
elif avg_score > 40:
    st.warning("MEDIUM RISK 🟡")
else:
    st.success("LOW RISK 🟢")

# ---------------- METRICS ----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Crimes", len(final_df))

with col2:
    st.metric("Avg Risk Score", f"{avg_score:.1f}")

with col3:
    st.metric("Selected City", city)

# ---------------- DATA PREVIEW ----------------
st.subheader("📊 Data Preview")
st.dataframe(final_df.head(20))

# ---------------- FOOTER ----------------
st.markdown("---")
st.write("Made by Priyanshu 🚀")
