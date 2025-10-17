import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Flood & Weather Analysis", layout="wide")

st.title("🌊 Flood & 🌦️ Weather Data Analysis (2014–2025)")
st.write("Upload both datasets below to visualize yearly and monthly comparisons!")

# --- File Upload ---
flood_file = st.file_uploader("📤 Upload Flood Dataset (CSV/XLSX)", type=["csv", "xlsx"])
weather_file = st.file_uploader("📤 Upload Weather Dataset (CSV/XLSX)", type=["csv", "xlsx"])

# ===== FLOOD DATASET =====
if flood_file is not None:
    try:
        if flood_file.name.endswith(".csv"):
            flood_df = pd.read_csv(flood_file)
        else:
            flood_df = pd.read_excel(flood_file)
        st.success("✅ Flood dataset loaded successfully!")

        # Detect date/year column
        date_cols = [col for col in flood_df.columns if 'date' in col.lower() or 'year' in col.lower()]
        if len(date_cols) == 0:
            st.warning("⚠️ No 'year' or 'date' column detected in flood dataset.")
        else:
            date_col = date_cols[0]

            # Only create year column if not existing
            if 'year' not in flood_df.columns:
                flood_df[date_col] = pd.to_datetime(flood_df[date_col], errors='coerce')
                flood_df['year'] = flood_df[date_col].dt.year

            if 'month' not in flood_df.columns:
                flood_df['month'] = pd.to_datetime(flood_df[date_col], errors='coerce').dt.month_name()

            numeric_cols = flood_df.select_dtypes(include='number').columns
            yearly_flood = flood_df.groupby('year')[numeric_cols].mean().reset_index()

            st.subheader("📊 Flood Data: Yearly Summary (2014–2025)")
            fig, ax = plt.subplots(figsize=(10, 5))
            yearly_flood.plot(x='year', kind='bar', ax=ax, title='Average Flood Data per Year')
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error loading Flood Dataset: {e}")

# ===== WEATHER DATASET =====
if weather_file is not None:
    try:
        if weather_file.name.endswith(".csv"):
            weather_df = pd.read_csv(weather_file)
        else:
            weather_df = pd.read_excel(weather_file)
        st.success("✅ Weather dataset loaded successfully!")

        # Detect date/year column
        date_cols = [col for col in weather_df.columns if 'date' in col.lower() or 'year' in col.lower()]
        if len(date_cols) == 0:
            st.warning("⚠️ No 'year' or 'date' column detected in weather dataset.")
        else:
            date_col = date_cols[0]

            if 'year' not in weather_df.columns:
                weather_df[date_col] = pd.to_datetime(weather_df[date_col], errors='coerce')
                weather_df['year'] = weather_df[date_col].dt.year

            if 'month' not in weather_df.columns:
                weather_df['month'] = pd.to_datetime(weather_df[date_col], errors='coerce').dt.month_name()

            numeric_cols = weather_df.select_dtypes(include='number').columns
            yearly_weather = weather_df.groupby('year')[numeric_cols].mean().reset_index()

            st.subheader("🌦️ Weather Data: Yearly Summary (2014–2025)")
            fig, ax = plt.subplots(figsize=(10, 5))
            yearly_weather.plot(x='year', kind='bar', ax=ax, title='Average Weather Data per Year', color='orange')
            st.pyplot(fig)

            # --- Comparison (Flood vs Weather) ---
            if flood_file is not None:
                st.subheader("🌧️ Flood vs Weather Comparison (Rainfall-based)")
                rain_col = None
                for col in weather_df.columns:
                    if 'rain' in col.lower():
                        rain_col = col
                        break

                water_col = None
                for col in flood_df.columns:
                    if 'water' in col.lower() or 'flood' in col.lower():
                        water_col = col
                        break

                if rain_col and water_col:
                    compare = pd.merge(
                        yearly_flood[['year', water_col]],
                        yearly_weather[['year', rain_col]],
                        on='year',
                        how='inner'
                    )
                    fig, ax = plt.subplots(figsize=(10, 5))
                    compare.plot(x='year', kind='bar', ax=ax, title='Yearly Flood Water Level vs Rainfall')
                    st.pyplot(fig)
                    st.dataframe(compare)
                else:
                    st.warning("⚠️ Comparison skipped — no 'rain' or 'water level' column found.")
    except Exception as e:
        st.error(f"Error loading Weather Dataset: {e}")
