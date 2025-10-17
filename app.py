"""
🌊 Flood & Weather Comparison App (2014–2025)
- Flood & Weather Datasets Visualization
- Auto preprocess month/day/year
- Yearly bar graphs
- Comparison of Rainfall vs Flood Occurrence
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Flood & Weather Comparison", layout="wide")

st.title("🌦️ Flood and Weather Data Analysis (2014–2025)")
st.markdown("Upload your **Flood** and **Weather** datasets below. The app will visualize trends and show a rainfall–flood comparison.")

# --- File Uploads ---
flood_file = st.file_uploader("📁 Upload Flood Dataset", type=["csv", "xlsx"])
weather_file = st.file_uploader("📁 Upload Weather Dataset", type=["csv", "xlsx"])

# --- Helper Functions ---
def load_data(file):
    if file is None:
        return None
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

def preprocess_data(df):
    df = df.copy()
    df.columns = df.columns.str.lower().str.strip()

    # Create 'year' column
    if 'year' not in df.columns:
        if {'month', 'day', 'year'}.issubset(df.columns):
            df['date'] = pd.to_datetime(df[['year', 'month', 'day']].astype(str).agg('-'.join, axis=1), errors='coerce')
            df['year'] = df['date'].dt.year
        else:
            for col in df.columns:
                if 'date' in col:
                    df['year'] = pd.to_datetime(df[col], errors='coerce').dt.year
                    break
    return df

# --- Load Data ---
flood_df = load_data(flood_file)
weather_df = load_data(weather_file)

# --- FLOOD DATA ---
if flood_df is not None:
    st.subheader("🌊 Flood Data Analysis")

    flood_df = preprocess_data(flood_df)
    numeric_cols = flood_df.select_dtypes(include=['number']).columns

    if 'year' in flood_df.columns:
        flood_summary = (
            flood_df.groupby('year')
            .agg({'water level':'mean'}) if 'water level' in flood_df.columns
            else flood_df.groupby('year')[numeric_cols].mean(numeric_only=True)
        ).reset_index()

        st.dataframe(flood_summary.style.highlight_max(axis=0), use_container_width=True)

        # Bar Graph
        st.subheader("📊 Flood Data (Average per Year)")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(flood_summary['year'], flood_summary.iloc[:, 1], color='royalblue', edgecolor='black')
        plt.title("Average Flood Values per Year (2014–2025)")
        plt.xlabel("Year")
        plt.ylabel("Average Water Level" if 'water level' in flood_df.columns else "Flood Metric")
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("⚠️ 'month', 'day', and 'year' columns not detected in flood dataset.")

# --- WEATHER DATA ---
if weather_df is not None:
    st.subheader("🌧️ Weather Data Analysis")

    weather_df = preprocess_data(weather_df)
    numeric_cols = weather_df.select_dtypes(include=['number']).columns

    if 'year' in weather_df.columns:
        # If rainfall or precipitation column exists, prioritize it
        rain_col = None
        for col in weather_df.columns:
            if 'rain' in col or 'precip' in col:
                rain_col = col
                break

        weather_summary = (
            weather_df.groupby('year')[numeric_cols].mean(numeric_only=True).reset_index()
        )

        st.dataframe(weather_summary.style.highlight_max(axis=0), use_container_width=True)

        # Bar Graph for Weather
        st.subheader("☁️ Weather Data (Average per Year)")
        fig, ax = plt.subplots(figsize=(10, 5))
        if rain_col:
            ax.bar(weather_summary['year'], weather_summary[rain_col], color='deepskyblue', edgecolor='black')
            plt.ylabel("Average Rainfall")
        else:
            ax.bar(weather_summary['year'], weather_summary.iloc[:, 1], color='deepskyblue', edgecolor='black')
            plt.ylabel("Weather Metric")
        plt.title("Average Weather Values per Year (2014–2025)")
        plt.xlabel("Year")
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("⚠️ 'month', 'day', and 'year' columns not detected in weather dataset.")

# --- COMPARISON GRAPH ---
if flood_df is not None and weather_df is not None and 'year' in flood_df.columns and 'year' in weather_df.columns:
    st.subheader("📈 Flood vs Weather Comparison (2014–2025)")

    # Create yearly flood & rainfall comparison
    flood_group = flood_df.groupby('year')['water level'].mean().reset_index() if 'water level' in flood_df.columns else flood_df.groupby('year').size().reset_index(name='flood_occurrences')

    rain_col = None
    for col in weather_df.columns:
        if 'rain' in col or 'precip' in col:
            rain_col = col
            break

    if rain_col:
        weather_group = weather_df.groupby('year')[rain_col].mean().reset_index()
    else:
        weather_group = weather_df.groupby('year').mean(numeric_only=True).reset_index()

    # Merge for comparison
    compare_df = pd.merge(flood_group, weather_group, on='year', how='inner', suffixes=('_flood', '_weather'))

    # Show combined dataframe
    st.dataframe(compare_df, use_container_width=True)

    # Dual-axis Bar Graph
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()

    ax1.bar(compare_df['year'], compare_df.iloc[:, 1], color='royalblue', alpha=0.6, label='Flood (Water Level)')
    ax2.plot(compare_df['year'], compare_df.iloc[:, 2], color='orange', marker='o', label='Rainfall')

    ax1.set_xlabel("Year")
    ax1.set_ylabel("Average Water Level", color='royalblue')
    ax2.set_ylabel("Average Rainfall", color='orange')
    plt.title("Flood vs Rainfall Comparison (2014–2025)")
    ax1.grid(axis='y', linestyle='--', alpha=0.6)
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))
    st.pyplot(fig)

st.markdown("---")
st.caption("🧩 Developed for Capstone: Data Mining Flood Pattern & Weather Analysis — 2025")
