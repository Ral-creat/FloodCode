import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Flood & Weather Analysis", layout="wide")

st.title("🌊 Flood & 🌦️ Weather Data Analysis (2014–2025)")
st.write("Upload both datasets below to visualize yearly and monthly comparisons!")

# --- File Upload ---
flood_file = st.file_uploader("📤 Upload Flood Dataset (CSV/XLSX)", type=["csv", "xlsx"])
weather_file = st.file_uploader("📤 Upload Weather Dataset (CSV/XLSX)", type=["csv", "xlsx"])

if flood_file is not None:
    try:
        if flood_file.name.endswith(".csv"):
            flood_df = pd.read_csv(flood_file)
        else:
            flood_df = pd.read_excel(flood_file)
        st.success("✅ Flood dataset loaded successfully!")

        # Auto-detect date/year columns
        date_cols = [col for col in flood_df.columns if 'date' in col.lower() or 'year' in col.lower()]
        if len(date_cols) == 0:
            st.warning("⚠️ No 'year' or 'date' column detected in flood dataset.")
        else:
            date_col = date_cols[0]
            flood_df[date_col] = pd.to_datetime(flood_df[date_col], errors='coerce')
            flood_df['year'] = flood_df[date_col].dt.year
            flood_df['month'] = flood_df[date_col].dt.month_name()

            numeric_cols = flood_df.select_dtypes(include='number').columns
            yearly_flood = flood_df.groupby('year')[numeric_cols].mean().reset_index()

            st.subheader("📊 Flood Data: Yearly Summary (2014–2025)")
            fig, ax = plt.subplots(figsize=(10, 5))
            yearly_flood.plot(x='year', kind='bar', ax=ax, title='Average Flood Data per Year')
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error loading Flood Dataset: {e}")

if weather_file is not None:
    try:
        if weather_file.name.endswith(".csv"):
            weather_df = pd.read_csv(weather_file)
        else:
            weather_df = pd.read_excel(weather_file)
        st.success("✅ Weather dataset loaded successfully!")

        # Auto-detect date/year columns
        date_cols = [col for col in weather_df.columns if 'date' in col.lower() or 'year' in col.lower()]
        if len(date_cols) == 0:
            st.warning("⚠️ No 'year' or 'date' column detected in weather dataset.")
        else:
            date_col = date_cols[0]
            weather_df[date_col] = pd.to_datetime(weather_df[date_col], errors='coerce')
            weather_df['year'] = weather_df[date_col].dt.year
            weather_df['month'] = weather_df[date_col].dt.month_name()

            numeric_cols = weather_df.select_dtypes(include='number').columns
            yearly_weather = weather_df.groupby('year')[numeric_cols].mean().reset_index()

            st.subheader("🌦️ Weather Data: Yearly Summary (2014–2025)")
            fig, ax = plt.subplots(figsize=(10, 5))
            yearly_weather.plot(x='year', kind='bar', ax=ax, title='Average Weather Data per Year', color='orange')
            st.pyplot(fig)

            # Compare flood vs rainfall (if rainfall column exists)
            if flood_file is not None:
                st.subheader("🌧️ Flood vs Weather Comparison (Rainfall-based)")
                if 'rainfall' in weather_df.columns and 'water_level' in flood_df.columns:
                    compare = pd.merge(
                        yearly_flood[['year', 'water_level']],
                        yearly_weather[['year', 'rainfall']],
                        on='year',
                        how='inner'
                    )
                    fig, ax = plt.subplots(figsize=(10, 5))
                    compare.plot(x='year', kind='bar', ax=ax, title='Yearly Flood Water Level vs Rainfall')
                    st.pyplot(fig)
                    st.write(compare)
                else:
                    st.warning("⚠️ Comparison skipped — columns 'rainfall' or 'water_level' not found.")
    except Exception as e:
        st.error(f"Error loading Weather Dataset: {e}")
