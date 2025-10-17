# ==============================
# Streamlit App: Flood Occurrence Visualization (2014–2025)
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
    
    # --- Data Cleaning ---
    df['month'] = df['month'].astype(str).str.strip().str.capitalize()
    df['year'] = df['year'].astype(int)

    # --- Count Flood Occurrences ---
    flood_counts = df.groupby(['year', 'month']).size().reset_index(name='flood_occurrences')

    # --- Sort months properly (Jan–Dec order) ---
    months_order = ['January','February','March','April','May','June','July','August','September','October','November','December']
    flood_counts['month'] = pd.Categorical(flood_counts['month'], categories=months_order, ordered=True)
    flood_counts = flood_counts.sort_values(['year', 'month'])

    # --- Visualization ---
    unique_years = sorted(flood_counts['year'].unique())

    st.write("### 📊 Flood Occurrences per Month (2014–2025)")

    cols = st.columns(3)
    for i, year in enumerate(unique_years):
        yearly_data = flood_counts[flood_counts['year'] == year]
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(yearly_data['month'], yearly_data['flood_occurrences'], color='skyblue', edgecolor='black')
        ax.set_title(f'Flood Occurrences - {year}')
        ax.set_xlabel('Month')
        ax.set_ylabel('Occurrences')
        ax.set_xticklabels(yearly_data['month'], rotation=45, ha='right')
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        with cols[i % 3]:
            st.pyplot(fig)
else:
    st.info("👆 Please upload the dataset to view the analysis.")
