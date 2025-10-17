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
   # ------------------ 🌦️ WEATHER DATA VISUALIZATION (Last Section) ------------------
st.markdown("---")
st.subheader("🌤️ Weather Data Summary (2014–2025)")

# Load and clean
weather_df = pd.read_excel(weather_file)
weather_df.columns = weather_df.columns.str.strip().str.lower()

# Detect Year & Month
w_month_col = [c for c in weather_df.columns if "month" in c][0]
w_year_col = [c for c in weather_df.columns if "year" in c][0]

# Clean
weather_df[w_month_col] = weather_df[w_month_col].astype(str).str.strip().str.capitalize()
weather_df[w_year_col] = pd.to_numeric(weather_df[w_year_col], errors="coerce")
weather_df = weather_df.dropna(subset=[w_year_col, w_month_col])
weather_df[w_year_col] = weather_df[w_year_col].astype(int)
weather_df = weather_df[weather_df[w_month_col].isin(valid_months)]

# Detect rainfall & temperature columns
rainfall_cols = [c for c in weather_df.columns if any(k in c for k in ["rain", "precip", "mm"])]
temp_cols = [c for c in weather_df.columns if any(k in c for k in ["temp", "°c", "temperature", "avg temp"])]

# Convert numeric values
for col in rainfall_cols + temp_cols:
    weather_df[col] = pd.to_numeric(weather_df[col], errors="coerce")

# Build summary
agg_dict = {}
for col in rainfall_cols + temp_cols:
    agg_dict[col] = "mean"

if not agg_dict:
    st.warning("⚠️ No valid rainfall or temperature columns found.")
    st.write("📋 Available columns:", weather_df.columns.tolist())
    weather_summary = pd.DataFrame(columns=[w_year_col, w_month_col])
else:
    weather_summary = (
        weather_df.groupby([w_year_col, w_month_col])
        .agg(agg_dict)
        .reset_index()
    )

weather_summary[w_month_col] = pd.Categorical(weather_summary[w_month_col], categories=valid_months, ordered=True)
weather_summary = weather_summary.sort_values([w_year_col, w_month_col])

# ============== VISUALIZATIONS ==============
st.subheader("📊 Monthly Rainfall and Temperature per Year (Separate Graphs)")

if not weather_summary.empty:
    unique_years = sorted(weather_summary[w_year_col].unique())

    # Separate Rainfall and Temperature Graphs
    for year in unique_years:
        yearly_data = weather_summary[weather_summary[w_year_col] == year]
        st.markdown(f"### 🌧️ Rainfall - {year}")

        # --- Rainfall line chart ---
        if rainfall_cols:
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(
                yearly_data[w_month_col],
                yearly_data[rainfall_cols[0]],
                color="royalblue",
                marker="o",
                linewidth=2,
            )
            ax.set_title(f"Monthly Rainfall ({year})")
            ax.set_xlabel("Month")
            ax.set_ylabel("Rainfall (mm)")
            ax.grid(True, linestyle="--", alpha=0.6)
            ax.set_xticklabels(yearly_data[w_month_col], rotation=45, ha="right")
            st.pyplot(fig)

        st.markdown(f"### 🌡️ Temperature - {year}")

        # --- Temperature line chart ---
        if temp_cols:
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(
                yearly_data[w_month_col],
                yearly_data[temp_cols[0]],
                color="darkred",
                marker="o",
                linewidth=2,
            )
            ax.set_title(f"Monthly Temperature ({year})")
            ax.set_xlabel("Month")
            ax.set_ylabel("Temperature (°C)")
            ax.grid(True, linestyle="--", alpha=0.6)
            ax.set_xticklabels(yearly_data[w_month_col], rotation=45, ha="right")
            st.pyplot(fig)

    # ========== YEARLY AVERAGE SUMMARY ==========
    st.subheader("📈 Yearly Average Rainfall and Temperature (2014–2025)")

    yearly_weather = (
        weather_df.groupby(w_year_col)[rainfall_cols + temp_cols]
        .mean(numeric_only=True)
        .reset_index()
    )

    # --- Rainfall Trend ---
    if rainfall_cols:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(
            yearly_weather[w_year_col],
            yearly_weather[rainfall_cols[0]],
            color="dodgerblue",
            marker="o",
            linewidth=2,
        )
        ax.set_title("Average Yearly Rainfall (mm)")
        ax.set_xlabel("Year")
        ax.set_ylabel("Rainfall (mm)")
        ax.grid(True, linestyle="--", alpha=0.6)
        st.pyplot(fig)

    # --- Temperature Trend ---
    if temp_cols:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(
            yearly_weather[w_year_col],
            yearly_weather[temp_cols[0]],
            color="firebrick",
            marker="o",
            linewidth=2,
        )
        ax.set_title("Average Yearly Temperature (°C)")
        ax.set_xlabel("Year")
        ax.set_ylabel("Temperature (°C)")
        ax.grid(True, linestyle="--", alpha=0.6)
        st.pyplot(fig)

else:
    st.info("No valid weather data available to visualize.")

