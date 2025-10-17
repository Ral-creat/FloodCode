# ==============================
# Streamlit App: Flood Occurrence Visualization (Auto-Detect Columns)
# ==============================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Flood Occurrence Visualization", layout="wide")

st.title("🌊 Flood Occurrence Visualization (2014–2025)")
st.write("This dashboard shows the monthly flood occurrences per year based on the uploaded dataset.")

# --- File Upload ---
uploaded_file = st.file_uploader("📂 Upload your FLOODDATASETFINAL.xlsx file", type=["xlsx"])

if uploaded_file is not None:
    # Load dataset
    df = pd.read_excel(uploaded_file)
    st.success("✅ File uploaded successfully!")

    st.write("### 🧾 Columns detected in your file:")
    st.write(list(df.columns))

    # Normalize column names (lowercase + strip spaces)
    df.columns = df.columns.str.strip().str.lower()

    # Check for possible matches
    month_col = [c for c in df.columns if "month" in c]
    year_col = [c for c in df.columns if "year" in c]

    if not month_col or not year_col:
        st.error("⚠️ Couldn't find 'month' or 'year' columns. Please check your Excel column names.")
    else:
        month_col = month_col[0]
        year_col = year_col[0]

        # --- Data Cleaning ---
        df[month_col] = df[month_col].astype(str).str.strip().str.capitalize()
        df[year_col] = df[year_col].astype(int)

        # --- Count Flood Occurrences ---
        flood_counts = df.groupby([year_col, month_col]).size().reset_index(name='flood_occurrences')

        # --- Sort months properly ---
        months_order = ['January','February','March','April','May','June','July','August','September','October','November','December']
        flood_counts[month_col] = pd.Categorical(flood_counts[month_col], categories=months_order, ordered=True)
        flood_counts = flood_counts.sort_values([year_col, month_col])

        # --- Visualization ---
        unique_years = sorted(flood_counts[year_col].unique())
        st.write("### 📊 Flood Occurrences per Month (2014–2025)")

        cols = st.columns(3)
        for i, year in enumerate(unique_years):
            yearly_data = flood_counts[flood_counts[year_col] == year]
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.bar(yearly_data[month_col], yearly_data['flood_occurrences'], color='skyblue', edgecolor='black')
            ax.set_title(f'Flood Occurrences - {year}')
            ax.set_xlabel('Month')
            ax.set_ylabel('Occurrences')
            ax.set_xticklabels(yearly_data[month_col], rotation=45, ha='right')
            ax.grid(axis='y', linestyle='--', alpha=0.5)
            with cols[i % 3]:
                st.pyplot(fig)
else:
    st.info("👆 Please upload the dataset to view the analysis.")
