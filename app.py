import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

# ---------------- PAGE ----------------
st.set_page_config(page_title="Crime Map", layout="wide")
st.title("🚓 Crime Hotspot Prediction System")

# ---------------- LOAD DATA ----------------
df = pd.read_csv("crime_data.csv")
df["Date"] = pd.to_datetime(df["Date"])

# ---------------- SIDEBAR ----------------
crime_type = st.sidebar.selectbox("Crime Type", df["Crime_Type"].unique())
city = st.sidebar.selectbox("City", ["Jaipur", "Delhi", "Mumbai"])

city_coords = {
    "Jaipur": [26.9124, 75.7873],
    "Delhi": [28.6139, 77.2090],
    "Mumbai": [19.0760, 72.8777]
}

filtered_df = df[df["Crime_Type"] == crime_type]
if filtered_df.empty:
    filtered_df = df.copy()

# ---------------- CONTROLS ----------------
st.subheader("🎛️ Controls")
hour = st.slider("Hour", 0, 23, 12)
temp = st.slider("Temperature", 10, 50, 25)
pop = st.slider("Population", 100, 1000, 500)

# ---------------- DYNAMIC SPREAD ----------------
spread = temp / 1000
final_df = filtered_df.copy()
np.random.seed(hour + temp + pop)

final_df["Latitude"] += np.random.normal(0, spread, len(final_df))
final_df["Longitude"] += np.random.normal(0, spread, len(final_df))

# ---------------- MAP ----------------
st.subheader("🗺️ Crime Hotspots Map")

center = city_coords[city]
crime_map = folium.Map(location=center, zoom_start=11)

for i, row in final_df.iterrows():
    lat = float(row["Latitude"])
    lon = float(row["Longitude"])

    # 🎯 per-dot risk logic
    risk_score = (hour * 2) + (temp * 0.5) + (pop * 0.01) + (i % 20)

    if risk_score > 60:
        color = "red"       # High
    elif risk_score > 40:
        color = "yellow"   # Medium
    else:
        color = "green"    # Low

    radius = max(4, pop / 180)

    folium.CircleMarker(
        location=[lat, lon],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.75,
        popup=f"Risk Score: {risk_score:.1f}"
    ).add_to(crime_map)

st_folium(crime_map, width=900, height=550)

# ---------------- GLOBAL RISK ----------------
avg_score = (hour * 2) + (temp * 0.5) + (pop * 0.01)

st.subheader("🚨 Risk Level")
if avg_score > 60:
    st.error("HIGH RISK 🔴")
elif avg_score > 40:
    st.warning("MEDIUM RISK 🟡")
else:
    st.success("LOW RISK 🟢")

# ---------------- PREVIEW ----------------
st.subheader("📊 Data Preview")
st.dataframe(final_df.head())

st.markdown("---")
st.write("Made by Priyanshu 🚀")
