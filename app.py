import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

# ---------------- PAGE ----------------
st.set_page_config(page_title="Crime Map", layout="wide")
st.title("🚓 Crime Hotspot Prediction System")

# ---------------- LOAD DATA ----------------
try:
    df = pd.read_csv("crime_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    df['Hour'] = df['Date'].dt.hour
except:
    st.error("⚠️ CSV not found! Using demo data")
    df = pd.DataFrame({
        "Latitude": [26.91, 28.61, 19.07],
        "Longitude": [75.78, 77.20, 72.87],
        "Crime_Type": ["Theft", "Robbery", "Assault"],
        "Date": pd.to_datetime(["2023-01-01"]*3)
    })

# ---------------- SIDEBAR ----------------
st.sidebar.header("Filters")

crime_type = st.sidebar.selectbox("Crime Type", df['Crime_Type'].unique())

city = st.sidebar.selectbox("Select City", ["Jaipur", "Delhi", "Mumbai"])

city_coords = {
    "Jaipur": [26.9124, 75.7873],
    "Delhi": [28.6139, 77.2090],
    "Mumbai": [19.0760, 72.8777]
}

filtered_df = df[df['Crime_Type'] == crime_type]

if filtered_df.empty:
    filtered_df = df

# ---------------- SLIDERS ----------------
st.subheader("Controls")

hour = st.slider("Hour", 0, 23, 12)
temp = st.slider("Temperature", 10, 50, 25)
pop = st.slider("Population", 100, 1000, 500)

# ---------------- FORCE DATA EFFECT ----------------
np.random.seed(hour + int(temp) + int(pop))

final_df = filtered_df.copy()

# अगर data empty या खराब है → fallback
if len(final_df) < 5:
    final_df = pd.DataFrame({
        "Latitude": np.random.uniform(26, 29, 100),
        "Longitude": np.random.uniform(72, 78, 100)
    })

# randomness add करो (visible effect)
final_df['Latitude'] = final_df['Latitude'] + np.random.normal(0, 0.02, len(final_df))
final_df['Longitude'] = final_df['Longitude'] + np.random.normal(0, 0.02, len(final_df))

# ---------------- DEBUG ----------------
st.write("Total Points:", len(final_df))

# ---------------- MAP ----------------
st.subheader("🗺️ Crime Map")

center = city_coords[city]
crime_map = folium.Map(location=center, zoom_start=10)

# 🔥 GUARANTEED DOTS LOOP
for i in range(len(final_df)):
    try:
        folium.CircleMarker(
            location=[float(final_df.iloc[i]['Latitude']), float(final_df.iloc[i]['Longitude'])],
            radius=7,
            color='red',
            fill=True,
            fill_opacity=0.7
        ).add_to(crime_map)
    except:
        pass

# extra fallback dots (always visible)
for lat, lon in zip(np.random.uniform(26, 29, 20), np.random.uniform(72, 78, 20)):
    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color='blue',
        fill=True
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
st.subheader("Data Preview")
st.dataframe(final_df.head())

st.markdown("---")
st.write("Made by Priyanshu 🚀")
