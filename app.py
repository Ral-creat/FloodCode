import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="🌊 Flood & 🌦️ Weather Data Analysis", layout="wide")

st.title("🌊 Flood & 🌦️ Weather Data Analysis (2014–2025)")
st.write("Upload both datasets below to visualize yearly summaries and comparisons based on rainfall and water level.")

# --- FILE UPLOAD ---
flood_file = st.file_uploader("📤 Upload Flood Dataset (CSV/XLSX)", type=["csv", "xlsx"])
weather_file = st.file_uploader("📤 Upload Weather Dataset (CSV/XLSX)", type=["csv", "xlsx"])

# --- Helper function to clean year/date columns safely ---
def extract_year(df):
    date_cols = [col for col in df.columns if 'date' in col.lower() or 'year' in col.lower()]
    if not date_cols:
        return None, "⚠️ No 'year' or 'date' column detected."
    col = date_cols[0]

    if 'date' in col.lower():
        df[col] = pd.to_datetime(df[col], errors='coerce')
        df['year'] = df[col].dt.year
    else:
        df['year'] = pd.to_numeric(df[col], errors='coerce')  # convert safely
    df = df.dropna(subset=['year'])  # remove empty year rows
    df['year'] = df['year'].astype(int)
    return df, None

# --- FLOOD DATA ---
if flood_file is not None:
    try:
        flood_df = pd.read_csv(flood_file) if flood_file.name.endswith(".csv") else pd.read_excel(flood_file)
        st.success("✅ Flood dataset loaded successfully!")

        flood_df, msg = extract_year(flood_df)
        if msg:
            st.warning(msg)
        else:
            numeric_cols = flood_df.select_dtypes(include='number').columns
            yearly_flood = flood_df.groupby('year')[numeric_cols].mean().reset_index()

            st.subheader("📊 Flood Data: Yearly Summary (2014–2025)")
            fig, ax = plt.subplots(figsize=(10, 5))
            yearly_flood.plot(x='year', kind='bar', ax=ax, title='Average Flood Data per Year', color='skyblue')
            st.pyplot(fig)
            st.dataframe(yearly_flood)

    except Exception as e:
        st.error(f"Error loading Flood Dataset: {e}")

# --- WEATHER DATA ---
if weather_file is not None:
    try:
        weather_df = pd.read_csv(weather_file) if weather_file.name.endswith(".csv") else pd.read_excel(weather_file)
        st.success("✅ Weather dataset loaded successfully!")

        weather_df, msg = extract_year(weather_df)
        if msg:
            st.warning(msg)
        else:
            numeric_cols = weather_df.select_dtypes(include='number').columns
            yearly_weather = weather_df.groupby('year')[numeric_cols].mean().reset_index()

            st.subheader("🌦️ Weather Data: Yearly Summary (2014–2025)")
            fig, ax = plt.subplots(figsize=(10, 5))
            yearly_weather.plot(x='year', kind='bar', ax=ax, title='Average Weather Data per Year', color='orange')
            st.pyplot(fig)
            st.dataframe(yearly_weather)

            # --- Comparison ---
            if flood_file is not None:
                st.subheader("🌧️ Flood vs Weather Comparison (Rainfall vs Water Level)")
                flood_col, rain_col = None, None

                # Try to auto-detect
                for col in flood_df.columns:
                    if 'water' in col.lower() or 'level' in col.lower():
                        flood_col = col
                        break
                for col in weather_df.columns:
                    if 'rain' in col.lower():
                        rain_col = col
                        break

                if flood_col and rain_col:
                    compare = pd.merge(
                        yearly_flood[['year', flood_col]],
                        yearly_weather[['year', rain_col]],
                        on='year',
                        how='inner'
                    )
                    fig, ax = plt.subplots(figsize=(10, 5))
                    compare.plot(
                        x='year',
                        kind='bar',
                        ax=ax,
                        title='Yearly Rainfall vs Flood Water Level',
                        color=['blue', 'orange']
                    )
                    st.pyplot(fig)
                    st.dataframe(compare)
                else:
                    st.warning("⚠️ Could not find rainfall or water level columns. Check dataset headers!")

    except Exception as e:
        st.error(f"Error loading Weather Dataset: {e}")
