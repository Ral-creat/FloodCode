"""
🌊 Flood & Weather Pattern Analysis (2014–2025)
- Upload separate datasets for Flood and Weather
- Auto preprocess & group by year
- Display yearly averages in bar graphs
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Flood & Weather Analysis", layout="wide")

st.title("🌦️ Flood and Weather Pattern Analysis (2014–2025)")
st.markdown("Upload your **Flood** and **Weather** datasets below to visualize yearly trends.")

# --- FILE UPLOADS ---
flood_file = st.file_uploader("📁 Upload Flood Dataset", type=["csv", "xlsx"])
weather_file = st.file_uploader("📁 Upload Weather Dataset", type=["csv", "xlsx"])

# --- HELPER FUNCTION ---
def load_data(file):
    if file is None:
        return None
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

# --- LOAD DATASETS ---
flood_df = load_data(flood_file)
weather_df = load_data(weather_file)

# ==================== FLOOD DATA SECTION ====================
if flood_df is not None:
    st.subheader("🌊 Flood Data Analysis")

    # Try detecting 'date' or 'year' column
    if 'year' not in flood_df.columns:
        date_col = None
        for col in flood_df.columns:
            if 'date' in col.lower():
                date_col = col
                break
        if date_col:
            flood_df['year'] = pd.to_datetime(flood_df[date_col], errors='coerce').dt.year

    # Filter only numeric columns
    numeric_cols = flood_df.select_dtypes(include=['number']).columns

    if 'year' in flood_df.columns:
        # Group by year and calculate mean
        flood_summary = (
            flood_df.groupby('year')[numeric_cols]
            .mean(numeric_only=True)
            .reset_index()
            .drop_duplicates(subset=['year'])
        )

        st.dataframe(flood_summary.style.highlight_max(axis=0), use_container_width=True)

        # --- BAR GRAPH ---
        st.subheader("📊 Flood Data (Average per Year)")
        fig, ax = plt.subplots(figsize=(10, 5))
        flood_summary.plot(
            x='year',
            y=numeric_cols,
            kind='bar',
            ax=ax,
            legend=True,
            width=0.8
        )
        plt.title("Average Flood Values per Year (2014–2025)")
        plt.xlabel("Year")
        plt.ylabel("Average Value")
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("⚠️ No 'year' or 'date' column detected in flood dataset.")


# ==================== WEATHER DATA SECTION ====================
if weather_df is not None:
    st.subheader("🌦️ Weather Data Analysis")

    # Detect or create 'year' column
    if 'year' not in weather_df.columns:
        date_col = None
        for col in weather_df.columns:
            if 'date' in col.lower():
                date_col = col
                break
        if date_col:
            weather_df['year'] = pd.to_datetime(weather_df[date_col], errors='coerce').dt.year

    # Select numeric columns
    numeric_cols = weather_df.select_dtypes(include=['number']).columns

    if 'year' in weather_df.columns:
        # Compute yearly averages
        weather_summary = (
            weather_df.groupby('year')[numeric_cols]
            .mean(numeric_only=True)
            .reset_index()
            .drop_duplicates(subset=['year'])
        )

        st.dataframe(weather_summary.style.highlight_max(axis=0), use_container_width=True)

        # --- BAR GRAPH ---
        st.subheader("📉 Weather Data (Average per Year)")
        fig, ax = plt.subplots(figsize=(10, 5))
        weather_summary.plot(
            x='year',
            y=numeric_cols,
            kind='bar',
            ax=ax,
            legend=True,
            width=0.8
        )
        plt.title("Average Weather Values per Year (2014–2025)")
        plt.xlabel("Year")
        plt.ylabel("Average Value")
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("⚠️ No 'year' or 'date' column detected in weather dataset.")

# ==================== END OF APP ====================
st.markdown("---")
st.caption("🧩 Developed for Data Mining Flood Pattern & Weather Analysis — 2025")
