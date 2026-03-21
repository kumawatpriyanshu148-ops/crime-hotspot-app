import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from sklearn.cluster import KMeans

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Crime Prediction", layout="wide")
st.title("🚓 Crime Hotspot Prediction System")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("crime_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    df['Hour'] = df['Date'].dt.hour
    return df

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.header("🔍 Filters")
crime_type = st.sidebar.selectbox("Crime Type", df['Crime_Type'].unique())
filtered_df = df[df['Crime_Type'] == crime_type]

st.metric("Total Crimes", len(filtered_df))

# ---------------- MAP ----------------
@st.cache_data
def create_map(data):
    X = data[['Latitude', 'Longitude']]
    kmeans = KMeans(n_clusters=4, random_state=42)
    data = data.copy()
    data['Cluster'] = kmeans.fit_predict(X)

    map_center = [data['Latitude'].mean(), data['Longitude'].mean()]
    crime_map = folium.Map(location=map_center, zoom_start=12)

    for _, row in data.iterrows():
        color = 'red' if row['Cluster'] == 0 else 'blue'
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=5,
            color=color,
            fill=True
        ).add_to(crime_map)

    return crime_map

st.subheader("🗺️ Crime Hotspots Map")
crime_map = create_map(filtered_df)
st_folium(crime_map, width=900)

# ---------------- SIMPLE PREDICTION (NO TF) ----------------
def simple_prediction(hour, temp, pop):
    return (hour * 2 + temp * 0.5 + pop * 0.01)

# ---------------- INPUT ----------------
st.subheader("🔮 Crime Prediction")

hour = st.slider("Select Hour", 0, 23, 12)
temperature = st.slider("Temperature (°C)", 10, 50, 25)
population = st.slider("Population Density", 100, 1000, 500)

# ---------------- PREDICT ----------------
if st.button("Predict"):
    result = simple_prediction(hour, temperature, population)

    st.success(f"Predicted Crime Level: {result:.2f}")

    if result > 50:
        st.error("HIGH RISK 🔴")
    elif result > 20:
        st.warning("MEDIUM RISK 🟡")
    else:
        st.success("LOW RISK 🟢")

# ---------------- DATA ----------------
st.subheader("📊 Data Preview")
st.dataframe(filtered_df.head())

# ---------------- FOOTER ----------------
st.markdown("---")
st.write("Made by Priyanshu 🚀")
