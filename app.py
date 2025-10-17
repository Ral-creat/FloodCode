"""
🌊 Flood & Weather Pattern Analysis (2014–2025)
- Upload separate datasets for Flood and Weather
- Auto preprocess using month, day, year columns
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

def preprocess_data(df):
    df = df.copy()

    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()

    # Try to create a 'year' column if missing
    if 'year' not in df.columns:
        if {'month', 'day', 'year'}.issubset(df.columns):
            # Combine to full date
            df['date'] = pd.to_datetime(df[['year', 'month', 'day']].astype(str).agg('-'.join, axis=1), errors='coerce')
            df['year'] = df['date'].dt.year
        else:
            # Try detect any column with 'date' in name
            for col in df.columns:
                if 'date' in col:
                    df['year'] = pd.to_datetime(df[col], errors='coerce').dt.year
                    break
    return df

# --- LOAD DATASETS ---
flood_df = load_data(flood_file)
weather_df = load_data(weather_file)

# ==================== FLOOD DATA SECTION ====================
if flood_df is not None:
    st.subheader("🌊 Flood Data Analysis")

    flood_df = preprocess_data(flood_df)
    numeric_cols = flood_df.select_dtypes(include=['number']).columns

    if 'year' in flood_df.columns:
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
        st.warning("⚠️ Columns for month/day/year not detected in flood dataset.")


# ==================== WEATHER DATA SECTION ====================
if weather_df is not None:
    st.subheader("🌦️ Weather Data Analysis")

    weather_df = preprocess_data(weather_df)
    numeric_cols = weather_df.select_dtypes(include=['number']).columns

    if 'year' in weather_df.columns:
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
        st.warning("⚠️ Columns for month/day/year not detected in weather dataset.")

# ==================== END OF APP ====================
st.markdown("---")
st.caption("🧩 Developed for Data Mining Flood Pattern & Weather Analysis — 2025")
