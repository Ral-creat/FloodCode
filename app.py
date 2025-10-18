import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Flood & Weather Comparison", layout="wide")

# ==============================
# CUSTOM CSS FOR VISUAL STYLE
# ==============================
st.markdown("""
<style>
/* ---------- General Layout ---------- */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg, #eef6ff 0%, #ffffff 100%);
    color: #1e293b;
    font-family: "Poppins", sans-serif;
}

/* ---------- Titles ---------- */
h1, h2, h3, h4 {
    font-weight: 600;
    color: #1e3a8a;
}
h1 {
    text-align: center;
    margin-bottom: 0.5rem;
}

/* ---------- Upload box ---------- */
[data-testid="stFileUploader"] {
    border: 2px dashed #3b82f6;
    border-radius: 12px;
    background-color: #f8fafc;
    padding: 10px;
}

/* ---------- Chart Containers ---------- */
.chart-box {
    background: white;
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    padding: 15px;
    margin-bottom: 25px;
    transition: all 0.3s ease-in-out;
}
.chart-box:hover {
    transform: scale(1.02);
    box-shadow: 0 6px 15px rgba(0,0,0,0.15);
}

/* ---------- Barangay Section ---------- */
.brgy-section {
    background: #f0f9ff;
    border-left: 5px solid #3b82f6;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
    transition: all 0.3s ease;
}
.brgy-section:hover {
    background: #dbeafe;
    transform: scale(1.01);
}

/* ---------- Chart titles ---------- */
.chart-title {
    text-align: center;
    font-weight: 600;
    color: #1d4ed8;
    margin-bottom: 5px;
}

/* ---------- Info Box ---------- */
[data-testid="stInfo"] {
    border-left: 4px solid #3b82f6 !important;
}

/* ---------- Remove chart shrink ---------- */
.css-1v0mbdj, .css-1aumxhk {
    overflow: visible !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# PAGE HEADER
# ==============================
st.title("🌊☁️ Flood and Weather Data Comparison (2014–2025)")
st.write("Upload both datasets below to visualize flood and weather data by year and month.")

# ==============================
# FILE UPLOAD SECTION
# ==============================
flood_file = st.file_uploader("📂 Upload Flood Dataset (Excel)", type=["xlsx"], key="flood")
weather_file = st.file_uploader("🌦️ Upload Weather Dataset (Excel)", type=["xlsx"], key="weather")

if flood_file and weather_file:
    # ==============================
    # LOAD & CLEAN FLOOD DATA
    # ==============================
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

    # ==============================
    # LOAD & CLEAN WEATHER DATA
    # ==============================
    weather_df = pd.read_excel(weather_file)
    weather_df.columns = weather_df.columns.str.strip().str.lower()

    w_month_col = [c for c in weather_df.columns if "month" in c][0]
    w_year_col = [c for c in weather_df.columns if "year" in c][0]

    weather_df[w_month_col] = weather_df[w_month_col].astype(str).str.strip().str.capitalize()
    weather_df[w_year_col] = pd.to_numeric(weather_df[w_year_col], errors='coerce')
    weather_df = weather_df.dropna(subset=[w_year_col, w_month_col])
    weather_df[w_year_col] = weather_df[w_year_col].astype(int)
    weather_df = weather_df[weather_df[w_month_col].isin(valid_months)]

    # ==============================
    # FLOOD VISUALIZATION
    # ==============================
    st.subheader("🌧️ Flood Occurrences per Year (2014–2025)")
    cols = st.columns(3)
    unique_years = sorted(flood_counts[year_col].unique())

    for i, year in enumerate(unique_years):
        yearly_data = flood_counts[flood_counts[year_col] == year]
        if yearly_data.empty:
            continue
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(yearly_data[month_col], yearly_data['flood_occurrences'],
               color='skyblue', edgecolor='black')
        ax.set_title(f'Flood Occurrences - {year}')
        ax.set_xlabel('Month')
        ax.set_ylabel('Occurrences')
        ax.set_xticklabels(yearly_data[month_col], rotation=45, ha='right')
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        with cols[i % 3]:
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.pyplot(fig)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==============================
    # BARANGAY SECTION
    # ==============================
    st.subheader("🏘️ Flood-Affected Barangays per Year")

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
            st.markdown(f'<div class="brgy-section"><h4>📅 {year} - Most Affected Barangays</h4>', unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(8, 3.5))
            ax.bar(yearly_data[brgy_col], yearly_data["flood_occurrences"],
                   color="cornflowerblue", edgecolor="black")
            ax.set_xlabel("Barangay")
            ax.set_ylabel("Flood Occurrences")
            ax.set_xticklabels(yearly_data[brgy_col], rotation=45, ha="right")
            ax.grid(axis='y', linestyle='--', alpha=0.5)
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            st.pyplot(fig)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==============================
    # WEATHER SUMMARY SECTION
    # ==============================
    st.markdown("---")
    st.subheader("🌤️ Weather Data Summary (2014–2025)")
    st.info("💡 Hover over any chart for animation effects.")

    rainfall_cols = [c for c in weather_df.columns if any(k in c for k in ["rain", "mm"])]
    temp_cols = [c for c in weather_df.columns if any(k in c for k in ["temp", "°c", "temperature"])]

    for col in rainfall_cols + temp_cols:
        weather_df[col] = pd.to_numeric(
            weather_df[col].astype(str).str.replace(r"[^\d\.\-]", "", regex=True), errors="coerce"
        )

    if rainfall_cols and temp_cols:
        yearly_weather = (
            weather_df.groupby(w_year_col)
            .agg({rainfall_cols[0]: "sum", temp_cols[0]: "mean"})
            .reset_index()
        )

        # yearly combined chart
        fig, ax1 = plt.subplots(figsize=(8, 4))
        ax1.bar(yearly_weather[w_year_col], yearly_weather[rainfall_cols[0]],
                color='skyblue', label='Total Rainfall (mm)')
        ax2 = ax1.twinx()
        ax2.plot(yearly_weather[w_year_col], yearly_weather[temp_cols[0]],
                 color='red', marker='o', label='Avg Temperature (°C)')
        ax1.set_xlabel("Year")
        ax1.set_ylabel("Rainfall (mm)", color='blue')
        ax2.set_ylabel("Temperature (°C)", color='red')
        ax1.set_title("Yearly Rainfall & Temperature (2014–2025)")
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.pyplot(fig)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.warning("⚠️ Please upload both Flood and Weather datasets to start visualization.")
