import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Crime Prediction", layout="wide")
st.title("🚓 Crime Hotspot Prediction System")

# ---------------- LOAD DATA ----------------
def load_data():
    df = pd.read_csv("crime_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    df['Hour'] = df['Date'].dt.hour
    return df

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.header("🔍 Filters")

crime_type = st.sidebar.selectbox("Crime Type", df['Crime_Type'].unique())

st.sidebar.header("📍 Select Location")

city = st.sidebar.selectbox(
    "Choose City",
    ["Jaipur", "Delhi", "Mumbai"]
)

city_coords = {
    "Jaipur": [26.9124, 75.7873],
    "Delhi": [28.6139, 77.2090],
    "Mumbai": [19.0760, 72.8777]
}

# ---------------- FILTER DATA ----------------
filtered_df = df[df['Crime_Type'] == crime_type]

if filtered_df.empty:
    filtered_df = df

st.metric("Total Crimes", len(filtered_df))

# ---------------- SHIFT DATA ----------------
def shift_data_to_city(data, center):
    data = data.copy()
    lat_shift = center[0] - data['Latitude'].mean()
    lon_shift = center[1] - data['Longitude'].mean()
    data['Latitude'] += lat_shift
    data['Longitude'] += lon_shift
    return data

# ---------------- INPUT ----------------
st.subheader("🔮 Crime Controls")

hour = st.slider("Select Hour", 0, 23, 12)
temperature = st.slider("Temperature (°C)", 10, 50, 25)
population = st.slider("Population Density", 100, 1000, 500)

# ---------------- APPLY EFFECT ----------------
def apply_dynamic_effect(data, hour, temp, pop):
    data = data.copy()
    np.random.seed(hour + int(temp) + int(pop))
    data['Latitude'] += np.random.normal(0, 0.01, len(data))
    data['Longitude'] += np.random.normal(0, 0.01, len(data))
    return data

map_center = city_coords[city]

shifted_df = shift_data_to_city(filtered_df, map_center)
final_df = apply_dynamic_effect(shifted_df, hour, temperature, population)

# ---------------- DEBUG ----------------
st.write("Total Points:", len(final_df))

# ---------------- CREATE MAP (FIXED) ----------------
def create_map(data, center):
    crime_map = folium.Map(location=center, zoom_start=10)

    for _, row in data.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=8,
            color='red',
            fill=True
        ).add_to(crime_map)

    return crime_map

st.subheader("🗺️ Crime Hotspots Map")

crime_map = create_map(final_df, map_center)
st_folium(crime_map, width=900)

# ---------------- PREDICTION ----------------
def simple_prediction(hour, temp, pop):
    return (hour * 2 + temp * 0.5 + pop * 0.01)

raw = simple_prediction(hour, temperature, population)

st.subheader("🚨 Risk Level")

if raw > 60:
    st.error("HIGH RISK 🔴")
elif raw > 30:
    st.warning("MEDIUM RISK 🟡")
else:
    st.success("LOW RISK 🟢")

# ---------------- DATA ----------------
st.subheader("📊 Data Preview")
st.dataframe(final_df.head())

# ---------------- FOOTER ----------------
st.markdown("---")
st.write("Made by Priyanshu 🚀")
