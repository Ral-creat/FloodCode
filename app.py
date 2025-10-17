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

    # Load and clean weather data again safely
    weather_df = pd.read_excel(weather_file)
    weather_df.columns = weather_df.columns.str.strip().str.lower()

    w_month_col = [c for c in weather_df.columns if "month" in c][0]
    w_year_col = [c for c in weather_df.columns if "year" in c][0]

    weather_df[w_month_col] = weather_df[w_month_col].astype(str).str.strip().str.capitalize()
    weather_df[w_year_col] = pd.to_numeric(weather_df[w_year_col], errors='coerce')
    weather_df = weather_df.dropna(subset=[w_year_col, w_month_col])
    weather_df[w_year_col] = weather_df[w_year_col].astype(int)
    weather_df = weather_df[weather_df[w_month_col].isin(valid_months)]

    # Detect rainfall and temperature columns
    rainfall_cols = [c for c in weather_df.columns if "rain" in c.lower()]
    temp_cols = [c for c in weather_df.columns if "temp" in c.lower() or "temperature" in c.lower()]

    # If no rainfall/temp columns found, pick numeric columns as fallback
    numeric_cols = weather_df.select_dtypes(include=["number"]).columns.tolist()
    if not rainfall_cols and numeric_cols:
        rainfall_cols = [numeric_cols[0]]
    if not temp_cols and len(numeric_cols) > 1:
        temp_cols = [numeric_cols[1]]

    # Group by Year & Month
    agg_dict = {}
    for col in rainfall_cols + temp_cols:
        if col in weather_df.columns:
            agg_dict[col] = 'mean'

    if not agg_dict:
        st.warning("⚠️ No numeric weather columns (rainfall or temperature) found in the uploaded file.")
        weather_summary = pd.DataFrame(columns=[w_year_col, w_month_col])
    else:
        weather_summary = (
            weather_df.groupby([w_year_col, w_month_col])
            .agg(agg_dict)
            .reset_index()
        )

    weather_summary[w_month_col] = pd.Categorical(
        weather_summary[w_month_col], categories=valid_months, ordered=True
    )
    weather_summary = weather_summary.sort_values([w_year_col, w_month_col])

    # ================= WEATHER VISUALS =================
    st.subheader("📊 Monthly Rainfall and Temperature per Year")

    if not weather_summary.empty:
        unique_years = sorted(weather_summary[w_year_col].unique())
        cols = st.columns(2)
        for i, year in enumerate(unique_years):
            yearly_data = weather_summary[weather_summary[w_year_col] == year]
            fig, ax1 = plt.subplots(figsize=(7, 4))
            ax1.set_title(f"Rainfall & Temperature - {year}")
            
            # Plot rainfall
            if rainfall_cols:
                ax1.bar(yearly_data[w_month_col], yearly_data[rainfall_cols[0]],
                        color='skyblue', edgecolor='black', label='Rainfall (mm)')
                ax1.set_ylabel("Rainfall (mm)", color='blue')
                ax1.tick_params(axis='y', labelcolor='blue')

            # Add temperature on secondary axis
            if temp_cols:
                ax2 = ax1.twinx()
                ax2.plot(yearly_data[w_month_col], yearly_data[temp_cols[0]],
                         color='red', marker='o', label='Temperature (°C)')
                ax2.set_ylabel("Temperature (°C)", color='red')
                ax2.tick_params(axis='y', labelcolor='red')

            ax1.set_xlabel("Month")
            ax1.set_xticklabels(yearly_data[w_month_col], rotation=45, ha='right')
            ax1.grid(axis='y', linestyle='--', alpha=0.5)
            ax1.yaxis.set_major_locator(MaxNLocator(integer=True))

            with cols[i % 2]:
                st.pyplot(fig)

        # ================= YEARLY WEATHER SUMMARY =================
        st.subheader("🌧️ Average Rainfall and Temperature per Year")

        yearly_weather = (
            weather_df.groupby(w_year_col)
            .agg(agg_dict)
            .reset_index()
        )

        fig, ax = plt.subplots(figsize=(8, 4))
        if rainfall_cols:
            ax.bar(yearly_weather[w_year_col], yearly_weather[rainfall_cols[0]],
                   color='cornflowerblue', label='Avg Rainfall (mm)')
        if temp_cols:
            ax.plot(yearly_weather[w_year_col], yearly_weather[temp_cols[0]],
                    color='darkred', marker='o', label='Avg Temperature (°C)')

        ax.set_xlabel("Year")
        ax.set_ylabel("Rainfall / Temperature")
        ax.set_title("Yearly Average Rainfall and Temperature (2014–2025)")
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("No valid weather data available to visualize.")
