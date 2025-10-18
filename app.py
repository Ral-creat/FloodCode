import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd

st.set_page_config(page_title="Flood & Weather Comparison", layout="wide")

# ------------------ 🌈 CSS Styling ------------------
st.markdown("""
<style>
/* General page background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f0f7ff 0%, #ffffff 100%);
}

/* Titles and subheaders */
h1, h2, h3, h4 {
    color: #1e3d59;
    font-family: 'Poppins', sans-serif;
}

/* Card-like hover container for charts */
.chart-container {
    transition: all 0.3s ease;
    border-radius: 15px;
    background-color: white;
    padding: 15px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
.chart-container:hover {
    transform: scale(1.03);
    box-shadow: 0px 6px 15px rgba(0,0,0,0.15);
}

/* Subheader separator */
hr {
    border: 1px solid #b5cde6;
    margin-top: 25px;
    margin-bottom: 25px;
}

/* Upload boxes */
[data-testid="stFileUploader"] {
    border: 2px dashed #3b82f6;
    border-radius: 10px;
    background-color: #f9fbff;
}

/* Add hover color to buttons */
button:hover {
    background-color: #2563eb !important;
    color: white !important;
}

/* Chart titles */
.chart-title {
    font-weight: 600;
    color: #1e40af;
    margin-bottom: 8px;
}

/* Flood barangay section hover */
.brgy-section {
    transition: background 0.3s ease, transform 0.3s ease;
    background: #f9fbff;
    border-radius: 12px;
    padding: 10px;
    margin-bottom: 15px;
}
.brgy-section:hover {
    background: #e0f2fe;
    transform: scale(1.01);
}
</style>
""", unsafe_allow_html=True)

# ------------------ PAGE HEADER ------------------
st.title("🌊☁️ Flood and Weather Data Comparison (2014–2025)")
st.write("Upload both datasets to view yearly and monthly flood and weather visualizations.")

# ------------------ FILE UPLOAD ------------------
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
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        with cols[i % 3]:
            with st.container():
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.pyplot(fig)
                st.markdown('</div>', unsafe_allow_html=True)

    # ------------------ Barangay Affected per Year ------------------
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
            st.markdown(f'<div class="brgy-section"><h4>📅 {year} - Flood-Affected Barangays</h4>', unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(9, 4))
            ax.bar(yearly_data[brgy_col], yearly_data["flood_occurrences"],
                   color="skyblue", edgecolor="black")
            ax.set_xlabel("Barangay")
            ax.set_ylabel("Flood Occurrences")
            ax.set_xticklabels(yearly_data[brgy_col], rotation=45, ha="right")
            ax.grid(axis='y', linestyle='--', alpha=0.5)
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            st.pyplot(fig)
            st.markdown('</div>', unsafe_allow_html=True)

# ------------------ WEATHER SECTION ------------------
st.markdown("---")
st.subheader("🌤️ Weather Data Summary (2014–2025)")
st.info("💡 Hover over charts to see animation effects.")
