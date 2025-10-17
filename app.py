"""
🌊 Flood & Weather Comparison Dashboard (Auto Header Detection)
Capstone: Data Mining Flood Pattern & Weather Analysis
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Flood & Weather Comparison", layout="wide")

st.title("🌦️ Flood and Weather Data Analysis (2014–2025)")
st.markdown("Upload your **Flood Dataset** and **Weather Dataset** below to visualize yearly trends and compare rainfall vs flood patterns.")

# --- File Upload ---
flood_file = st.file_uploader("📁 Upload Flood Dataset", type=["csv", "xlsx"])
weather_file = st.file_uploader("🌧️ Upload Weather Dataset", type=["csv", "xlsx"])

# --- Helper Functions ---
def load_data(file):
    if file is None:
        return None
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

def preprocess(df):
    df = df.copy()
    df.columns = df.columns.str.lower().str.strip()

    # Try to create a full date if month/day/year exist
    if {'month', 'day', 'year'}.issubset(df.columns):
        df['date'] = pd.to_datetime(df[['year', 'month', 'day']].astype(str).agg('-'.join, axis=1), errors='coerce')
        df['year'] = df['date'].dt.year
    elif 'date' in df.columns:
        df['year'] = pd.to_datetime(df['date'], errors='coerce').dt.year

    return df

# --- Load Data ---
f
