import streamlit as st
import pandas as pd
import numpy as np
import pickle
import folium
from streamlit_folium import st_folium
from tensorflow.keras.models import load_model
from sklearn.cluster import KMeans

# Title
st.title("🚓 Crime Hotspot Prediction App")

# Load model
model = load_model("crime_model.h5", compile=False)

# Load scaler
with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

# Load data
df = pd.read_csv("crime_data.csv")
df['Date'] = pd.to_datetime(df['Date'])
df['Hour'] = df['Date'].dt.hour

# Show data
st.subheader("📊 Crime Data")
st.dataframe(df.head())

# Clustering
X = df[['Latitude', 'Longitude']]
kmeans = KMeans(n_clusters=4)
df['Cluster'] = kmeans.fit_predict(X)

# Map
st.subheader("🗺️ Crime Hotspots Map")

map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
crime_map = folium.Map(location=map_center, zoom_start=12)

for _, row in df.iterrows():
    color = 'red' if row['Cluster']==0 else 'blue'
    
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=5,
        color=color,
        fill=True
    ).add_to(crime_map)

st_folium(crime_map)

# Prediction
st.subheader("🔮 Prediction")

val1 = st.number_input("Enter value 1")
val2 = st.number_input("Enter value 2")
val3 = st.number_input("Enter value 3")

if st.button("Predict"):
    input_data = np.array([[val1],[val2],[val3]])
    input_scaled = scaler.transform(input_data)
    input_scaled = input_scaled.reshape(1,3,1)

    pred = model.predict(input_scaled)
    result = scaler.inverse_transform(pred)

    st.success(f"Predicted Crime: {result[0][0]}")

    if result > 50:
        st.error("HIGH RISK 🔴")
    elif result > 20:
        st.warning("MEDIUM RISK 🟡")
    else:
        st.success("LOW RISK 🟢")