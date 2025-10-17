# ===============================================
# Streamlit App: Flood & Weather Comparison (2014–2025)
# ===============================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

    # Detect year & month columns
    w_month_col = [c for c in weather_df.columns if "month" in c][0]
    w_year_col = [c for c in weather_df.columns if "year" in c][0]

    weather_df[w_month_col] = weather_df[w_month_col].astype(str).str.strip().str.capitalize()
    weather_df[w_year_col] = pd.to_numeric(weather_df[w_year_col], errors='coerce')
    weather_df = weather_df.dropna(subset=[w_year_col, w_month_col])
    weather_df[w_year_col] = weather_df[w_year_col].astype(int)
    weather_df = weather_df[weather_df[w_month_col].isin(valid_months)]

    # Select numeric columns
    numeric_cols = weather_df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    # Average weather per year – FIXED VERSION
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
        with cols[i % 3]:
            st.pyplot(fig)
               # ------------------ Barangay Affected per Year ------------------
    st.subheader("🏘️ Barangay Affected per Year")

    # Try to detect barangay column
    barangay_cols = [c for c in flood_df.columns if "barangay" in c.lower()]
    if barangay_cols:
        brgy_col = barangay_cols[0]

        # Include all barangays per year (even with 0 occurrences)
        all_years = sorted(flood_df[year_col].unique())
        all_barangays = sorted(flood_df[brgy_col].dropna().unique())

        # Create full cross-join for all years × barangays
        full_combo = pd.MultiIndex.from_product(
            [all_years, all_barangays],
            names=[year_col, brgy_col]
        ).to_frame(index=False)

        # Count flood occurrences
        brgy_yearly = flood_df.groupby([year_col, brgy_col]).size().reset_index(name="flood_occurrences")

        # Merge to include missing barangays (fill zeros)
        brgy_yearly = pd.merge(full_combo, brgy_yearly, on=[year_col, brgy_col], how="left").fillna(0)
        brgy_yearly["flood_occurrences"] = brgy_yearly["flood_occurrences"].astype(int)

        # --- Graph per Year ---
        for year in all_years:
            yearly_brgy = brgy_yearly[brgy_yearly[year_col] == year]
            st.markdown(f"### 📅 {year} - Flood Occurrences per Barangay")
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar(yearly_brgy[brgy_col], yearly_brgy["flood_occurrences"],
                   color="lightcoral", edgecolor="black")
            ax.set_xlabel("Barangay")
            ax.set_ylabel("Flood Occurrences")
            ax.set_title(f"Barangays Affected - {year}")
            ax.set_xticklabels(yearly_brgy[brgy_col], rotation=45, ha="right")
            ax.grid(axis='y', linestyle='--', alpha=0.5)
            st.pyplot(fig)

        # --- List Barangays Affected per Year ---
        st.markdown("### 📋 List of Barangays Affected per Year")
        year_groups = brgy_yearly.groupby(year_col)[brgy_col].apply(lambda x: ', '.join(sorted(set(x)))).reset_index()
        for _, row in year_groups.iterrows():
            st.markdown(f"**{row[year_col]}:** {row[brgy_col]}")

        # --- Summary: Most Affected Barangays Overall ---
        st.subheader("🔥 Summary: Most Frequently Flooded Barangays (2014–2025)")
        brgy_summary = brgy_yearly.groupby(brgy_col)["flood_occurrences"].sum().reset_index()
        brgy_summary = brgy_summary.sort_values("flood_occurrences", ascending=False)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(brgy_summary[brgy_col], brgy_summary["flood_occurrences"],
               color="tomato", edgecolor="black")
        ax.set_xlabel("Barangay")
        ax.set_ylabel("Total Flood Occurrences (2014–2025)")
        ax.set_title("Total Flood Occurrences by Barangay")
        ax.set_xticklabels(brgy_summary[brgy_col], rotation=45, ha="right")
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        st.pyplot(fig)

        st.dataframe(brgy_summary)
    else:
        st.warning("⚠️ No 'Barangay' column detected in flood dataset.")


    # ------------------ Weather Visuals ------------------
    st.subheader("🌡️ Weather Summary (2014–2025)")
    st.dataframe(weather_summary)

    # ------------------ Comparison Summary ------------------
    st.subheader("📊 Flood vs Weather Comparison")
    flood_summary = flood_counts.groupby(year_col)['flood_occurrences'].sum().reset_index()
    flood_summary.rename(columns={year_col: "year"}, inplace=True)
    weather_summary.rename(columns={w_year_col: "year"}, inplace=True)

    comparison = pd.merge(flood_summary, weather_summary, on="year", how="outer").fillna(0)
    st.dataframe(comparison)

    st.write("### 🔍 Insights")
    st.write("""
    - **Flood Occurrences:** Total floods per year.
    - **Weather Summary:** Average weather measurements per year.
    - **Comparison Table:** Combines flood frequency with yearly average weather data.
    """)
else:
    st.info("👆 Please upload both datasets to generate the analysis.")
