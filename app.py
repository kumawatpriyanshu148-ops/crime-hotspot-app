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
df['Date'] = pd.to_datetime(df['Date'])
df['Hour'] = df['Date'].dt.hour

# ---------------- SIDEBAR ----------------
crime_type = st.sidebar.selectbox("Crime Type", df['Crime_Type'].unique())
city = st.sidebar.selectbox("City", ["Jaipur", "Delhi", "Mumbai"])

city_coords = {
    "Jaipur": [26.9124, 75.7873],
    "Delhi": [28.6139, 77.2090],
    "Mumbai": [19.0760, 72.8777]
}

filtered_df = df[df['Crime_Type'] == crime_type]
if filtered_df.empty:
    filtered_df = df

# ---------------- SESSION STATE (IMPORTANT) ----------------
if "map_data" not in st.session_state:
    st.session_state.map_data = filtered_df.copy()

# ---------------- SLIDERS ----------------
st.subheader("Controls")

hour = st.slider("Hour", 0, 23, 12)
temp = st.slider("Temperature", 10, 50, 25)
pop = st.slider("Population", 100, 1000, 500)

# ---------------- APPLY EFFECT ONLY ON BUTTON ----------------
if st.button("Update Map"):
    new_df = filtered_df.copy()

    spread = temp / 1000
    new_df['Latitude'] += np.random.normal(0, spread, len(new_df))
    new_df['Longitude'] += np.random.normal(0, spread, len(new_df))

    st.session_state.map_data = new_df

# ---------------- MAP ----------------
st.subheader("🗺️ Crime Hotspots Map")

center = city_coords[city]
crime_map = folium.Map(location=center, zoom_start=10)

data = st.session_state.map_data

for i in range(len(data)):
    lat = float(data.iloc[i]['Latitude'])
    lon = float(data.iloc[i]['Longitude'])

    # Color by hour
    if hour > 18:
        color = "red"
    elif hour > 10:
        color = "yellow"
    else:
        color = "blue"

    radius = pop / 150

    folium.CircleMarker(
        location=[lat, lon],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7
    ).add_to(crime_map)

st_folium(crime_map, width=900, height=500)

# ---------------- RISK ----------------
def predict(h, t, p):
    return h*2 + t*0.5 + p*0.01

score = predict(hour, temp, pop)

st.subheader("🚨 Risk Level")

if score > 60:
    st.error("HIGH RISK 🔴")
elif score > 30:
    st.warning("MEDIUM RISK 🟡")
else:
    st.success("LOW RISK 🟢")

# ---------------- DATA ----------------
st.subheader("📊 Data Preview")
st.dataframe(data.head())
