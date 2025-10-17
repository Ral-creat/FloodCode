import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator  # 👈 added this

st.set_page_config(page_title="Flood & Weather Comparison", layout="wide")

st.title("🌊☁️ Flood and Weather Data Comparison (2014–2025)")
st.write("Upload both datasets to view yearly and monthly flood and weather visualizations.")

# Upload files
flood_file = st.file_uploader("📂 Upload Flood Dataset (Excel)", type=["xlsx"], key="flood")
weather_file = st.file_uploader("🌦️ Upload Weather Dataset (Excel)", type=["xlsx"], key="weather")

if flood_file and weather_file:
    # ------------------ Load & Clean Flood Data ------------------
    flood_df = pd.read_excel(flood_file)
    flood_df.columns = flood_df.columns.str.strip().str.lower()

    month_col = [c for c in flood_df.columns if "month" in c][0]
    year_col = [c for c in flood_df.columns if "year" in c][0]

    flood_df[month_col] = flood_df[month_col].astype(str).str.strip().str.capitalize()
    flood_df[year_col] = pd.to_numeric(flood_df[year_col], errors='coerce')
    flood_df = flood_df.dropna(subset=[year_col, month_col])
    flood_df[year_col] = flood_df[year_col].astype(int)

    valid_months = [
        'January','February','March','April','May','June',
        'July','August','September','October','November','December'
    ]
    flood_df = flood_df[flood_df[month_col].isin(valid_months)]

    flood_counts = flood_df.groupby([year_col, month_col]).size().reset_index(name='flood_occurrences')
    flood_counts[month_col] = pd.Categorical(flood_counts[month_col], categories=valid_months, ordered=True)
    flood_counts = flood_counts.sort_values([year_col, month_col])

    # ------------------ Load & Clean Weather Data ------------------
    weather_df = pd.read_excel(weather_file)
    weather_df.columns = weather_df.columns.str.strip().str.lower()

    w_month_col = [c for c in weather_df.columns if "month" in c][0]
    w_year_col = [c for c in weather_df.columns if "year" in c][0]

    weather_df[w_month_col] = weather_df[w_month_col].astype(str).str.strip().str.capitalize()
    weather_df[w_year_col] = pd.to_numeric(weather_df[w_year_col], errors='coerce')
    weather_df = weather_df.dropna(subset=[w_year_col, w_month_col])
    weather_df[w_year_col] = weather_df[w_year_col].astype(int)
    weather_df = weather_df[weather_df[w_month_col].isin(valid_months)]

    numeric_cols = weather_df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    weather_summary = weather_df.groupby(w_year_col, as_index=False)[numeric_cols].mean(numeric_only=True)

    # ------------------ Flood Visuals ------------------
    st.subheader("🌧️ Flood Occurrences per Year (2014–2025)")
    cols = st.columns(3)
    unique_years = sorted(flood_counts[year_col].unique())

    for i, year in enumerate(unique_years):
        yearly_data = flood_counts[flood_counts[year_col] == year]
        if yearly_data.empty:
            continue
        fig, ax = plt.subplots(figsize=(5,3))
        ax.bar(yearly_data[month_col], yearly_data['flood_occurrences'],
               color='skyblue', edgecolor='black')
        ax.set_title(f'Flood Occurrences - {year}')
        ax.set_xlabel('Month')
        ax.set_ylabel('Occurrences')
        ax.set_xticklabels(yearly_data[month_col], rotation=45, ha='right')
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))  # 👈 ensures whole number y-axis
        with cols[i % 3]:
            st.pyplot(fig)

  # ------------------ Barangay Affected per Year (Top 5 List) ------------------
    st.subheader("🏘️ Barangay Affected per Year")

    barangay_cols = [c for c in flood_df.columns if "barangay" in c.lower()]
    if barangay_cols:
        brgy_col = barangay_cols[0]
        brgy_yearly = (
            flood_df.groupby([year_col, brgy_col])
            .size()
            .reset_index(name="flood_occurrences")
            .sort_values([year_col, "flood_occurrences"], ascending=[True, False])
        )

        all_years = sorted(brgy_yearly[year_col].unique())
        for year in all_years:
            yearly_data = brgy_yearly[brgy_yearly[year_col] == year]
            if yearly_data.empty:
                continue
            st.markdown(f"### 📅 {year} - Flood-Affected Barangays")
            fig, ax = plt.subplots(figsize=(9, 4))
            ax.bar(
                yearly_data[brgy_col],
                yearly_data["flood_occurrences"],
                color="skyblue",
                edgecolor="black"
            )
            ax.set_xlabel("Barangay")
            ax.set_ylabel("Flood Occurrences")
            ax.set_title(f"Flood-Affected Barangays - {year}")
            ax.set_xticklabels(yearly_data[brgy_col], rotation=45, ha="right")
            ax.grid(axis='y', linestyle='--', alpha=0.5)
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))  # 👈 also fix decimals here
            st.pyplot(fig)
# ------------------ 🌦️ WEATHER DATA VISUALIZATION (Daily) ------------------
st.markdown("---")
st.subheader("🌤️ Daily Weather Data Summary (2014–2025)")

# Load Excel
weather_df = pd.read_excel(weather_file)
weather_df.columns = weather_df.columns.str.strip().str.lower()

# Detect possible date/day/year columns
date_cols = [c for c in weather_df.columns if "date" in c or "day" in c]
year_cols = [c for c in weather_df.columns if "year" in c]

if date_cols:
    date_col = date_cols[0]
    weather_df[date_col] = pd.to_datetime(weather_df[date_col], errors="coerce")
else:
    st.error("⚠️ No date or day column found. Please include one in your Excel file.")
    st.stop()

# Detect numeric rainfall and temperature columns
rainfall_cols = [c for c in weather_df.columns if any(k in c for k in ["rain", "precip", "mm"])]
temp_cols = [c for c in weather_df.columns if any(k in c for k in ["temp", "°c", "temperature"])]

for col in rainfall_cols + temp_cols:
    weather_df[col] = pd.to_numeric(weather_df[col], errors="coerce")

if not rainfall_cols and not temp_cols:
    st.warning("⚠️ No rainfall or temperature columns detected. Please verify Excel headers.")
    st.write("📋 Available columns:", weather_df.columns.tolist())
    st.stop()

# Clean dataframe
weather_df = weather_df.dropna(subset=[date_col])
weather_df = weather_df.sort_values(by=date_col)

# ========== 📈 DAILY RAINFALL GRAPH ==========
if rainfall_cols:
    st.subheader("🌧️ Daily Rainfall (mm)")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(weather_df[date_col], weather_df[rainfall_cols[0]],
            color='royalblue', marker='', linewidth=1.5)
    ax.set_title("Daily Rainfall Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Rainfall (mm)")
    ax.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig)

# ========== 🌡️ DAILY TEMPERATURE GRAPH ==========
if temp_cols:
    st.subheader("🌡️ Daily Temperature (°C)")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(weather_df[date_col], weather_df[temp_cols[0]],
            color='darkred', marker='', linewidth=1.5)
    ax.set_title("Daily Temperature Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Temperature (°C)")
    ax.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig)

# ========== 📊 SUMMARY STATS ==========
st.subheader("📋 Weather Summary Statistics")

summary_data = {
    "Average Rainfall (mm)": weather_df[rainfall_cols[0]].mean() if rainfall_cols else None,
    "Max Rainfall (mm)": weather_df[rainfall_cols[0]].max() if rainfall_cols else None,
    "Average Temperature (°C)": weather_df[temp_cols[0]].mean() if temp_cols else None,
    "Max Temperature (°C)": weather_df[temp_cols[0]].max() if temp_cols else None
}

summary_df = pd.DataFrame(summary_data, index=["Values"])
st.dataframe(summary_df.T)


