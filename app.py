"""
🌊 Flood & Weather Interactive Dashboard (2014–2025)
- Flood & Weather datasets visualization
- Auto preprocess month/day/year
- Yearly interactive bar graphs
- Flood vs Rainfall comparison with hover effects
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Flood & Weather Dashboard", layout="wide")

st.title("🌦️ Flood and Weather Interactive Analysis (2014–2025)")
st.markdown("Upload your **Flood** and **Weather** datasets below to visualize yearly trends and compare rainfall vs flood occurrence.")

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
        if 'water level' in flood_df.columns:
            flood_summary = flood_df.groupby('year')['water level'].mean().reset_index()
        else:
            flood_summary = flood_df.groupby('year').size().reset_index(name='flood_occurrences')

        st.dataframe(flood_summary, use_container_width=True)

        # Interactive Bar Graph
        fig = px.bar(
            flood_summary,
            x='year',
            y=flood_summary.columns[1],
            color_discrete_sequence=['royalblue'],
            title="🌊 Average Flood Data per Year (2014–2025)",
            labels={flood_summary.columns[1]: "Average Water Level" if 'water level' in flood_df.columns else "Flood Occurrences"},
            text_auto=True
        )
        fig.update_layout(xaxis_title="Year", yaxis_title="Flood Value", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ 'month', 'day', and 'year' columns not detected in flood dataset.")

# --- WEATHER DATA ---
if weather_df is not None:
    st.subheader("🌧️ Weather Data Analysis")

    weather_df = preprocess_data(weather_df)
    numeric_cols = weather_df.select_dtypes(include=['number']).columns

    if 'year' in weather_df.columns:
        rain_col = None
        for col in weather_df.columns:
            if 'rain' in col or 'precip' in col:
                rain_col = col
                break

        if rain_col:
            weather_summary = weather_df.groupby('year')[rain_col].mean().reset_index()
        else:
            weather_summary = weather_df.groupby('year')[numeric_cols].mean().reset_index()

        st.dataframe(weather_summary, use_container_width=True)

        # Interactive Bar Graph
        fig = px.bar(
            weather_summary,
            x='year',
            y=weather_summary.columns[1],
            color_discrete_sequence=['deepskyblue'],
            title="🌧️ Average Weather Data per Year (2014–2025)",
            labels={weather_summary.columns[1]: "Average Rainfall" if rain_col else "Weather Value"},
            text_auto=True
        )
        fig.update_layout(xaxis_title="Year", yaxis_title="Weather Metric", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ 'month', 'day', and 'year' columns not detected in weather dataset.")

# --- COMPARISON GRAPH ---
if (
    flood_df is not None
    and weather_df is not None
    and 'year' in flood_df.columns
    and 'year' in weather_df.columns
):
    st.subheader("📈 Flood vs Rainfall Comparison (2014–2025)")

    # Flood Summary
    if 'water level' in flood_df.columns:
        flood_group = flood_df.groupby('year')['water level'].mean().reset_index()
        flood_group.rename(columns={'water level': 'Average Water Level'}, inplace=True)
    else:
        flood_group = flood_df.groupby('year').size().reset_index(name='Flood Occurrences')

    # Rain Summary
    rain_col = None
    for col in weather_df.columns:
        if 'rain' in col or 'precip' in col:
            rain_col = col
            break

    if rain_col:
        weather_group = weather_df.groupby('year')[rain_col].mean().reset_index()
        weather_group.rename(columns={rain_col: 'Average Rainfall'}, inplace=True)
    else:
        weather_group = weather_df.groupby('year').mean().reset_index()

    # Merge
    compare_df = pd.merge(flood_group, weather_group, on='year', how='inner')

    st.dataframe(compare_df, use_container_width=True)

    # Interactive Comparison Chart
    fig = px.bar(
        compare_df,
        x='year',
        y=compare_df.columns[1],
        color_discrete_sequence=['royalblue'],
        opacity=0.7,
        title="🌊 Flood vs 🌧️ Rainfall Comparison (2014–2025)",
        labels={compare_df.columns[1]: "Flood Value"},
    )

    # Add Rainfall Line
    fig.add_scatter(
        x=compare_df['year'],
        y=compare_df[compare_df.columns[2]],
        mode='lines+markers',
        name='Average Rainfall',
        line=dict(color='orange', width=3),
        marker=dict(size=8)
    )

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Value",
        template="plotly_white",
        legend_title_text="Legend",
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("🧩 Developed for Capstone: Data Mining Flood Pattern & Weather Analysis — 2025")
