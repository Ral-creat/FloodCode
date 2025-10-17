import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Flood & Weather Yearly Analysis", layout="wide")

st.title("🌊 Flood and Weather Data Comparison (2014–2025)")

# --- File uploaders ---
st.sidebar.header("📂 Upload Datasets")
flood_file = st.sidebar.file_uploader("Upload Flood Dataset (CSV/XLSX)", type=["csv", "xlsx"])
weather_file = st.sidebar.file_uploader("Upload Weather Dataset (CSV/XLSX)", type=["csv", "xlsx"])

if flood_file and weather_file:
    # --- Load data ---
    if flood_file.name.endswith(".csv"):
        flood_df = pd.read_csv(flood_file)
    else:
        flood_df = pd.read_excel(flood_file)

    if weather_file.name.endswith(".csv"):
        weather_df = pd.read_csv(weather_file)
    else:
        weather_df = pd.read_excel(weather_file)

    # --- Clean Flood Data ---
    flood_df.columns = flood_df.columns.str.strip().str.lower()
    if 'year' not in flood_df.columns:
        st.error("⚠️ Flood dataset must have a 'year' column.")
        st.stop()
    flood_df['year'] = pd.to_numeric(flood_df['year'], errors='coerce')
    flood_df = flood_df.dropna(subset=['year'])
    flood_df['year'] = flood_df['year'].astype(int)

    if 'month' in flood_df.columns:
        flood_df['month'] = flood_df['month'].astype(str).str.strip().str.capitalize()

    # Count flood occurrences per year
    flood_summary = flood_df.groupby('year').size().reset_index(name='flood_occurrences')

    # --- Clean Weather Data ---
    weather_df.columns = weather_df.columns.str.strip().str.lower()
    if 'year' not in weather_df.columns:
        st.error("⚠️ Weather dataset must have a 'year' column.")
        st.stop()
    weather_df['year'] = pd.to_numeric(weather_df['year'], errors='coerce')
    weather_df = weather_df.dropna(subset=['year'])
    weather_df['year'] = weather_df['year'].astype(int)

    if 'month' in weather_df.columns:
        weather_df['month'] = weather_df['month'].astype(str).str.strip().str.capitalize()

    # Example: Average rainfall (mm) or temperature per year
    numeric_cols = weather_df.select_dtypes(include='number').columns
    if len(numeric_cols) > 0:
        weather_summary = weather_df.groupby('year')[numeric_cols].mean().reset_index()
    else:
        st.warning("⚠️ Weather dataset has no numeric columns to summarize.")
        weather_summary = pd.DataFrame({'year': [], 'rainfall': []})

    # --- Merge the summaries ---
    comparison_df = pd.merge(flood_summary, weather_summary, on='year', how='outer').sort_values('year')

    # --- Visualization: Yearly Bar Graphs ---
    st.subheader("📊 Yearly Flood and Weather Summary (2014–2025)")
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.bar(comparison_df['year'], comparison_df['flood_occurrences'], color='skyblue', label='Flood Occurrences')
    ax1.set_ylabel("Flood Occurrences", color='blue')
    ax1.set_xlabel("Year")

    # Add rainfall/temperature on secondary axis if available
    if 'rainfall' in weather_summary.columns:
        ax2 = ax1.twinx()
        ax2.plot(comparison_df['year'], comparison_df['rainfall'], color='orange', marker='o', label='Avg Rainfall')
        ax2.set_ylabel("Average Rainfall (mm)", color='orange')
    elif len(numeric_cols) > 0:
        col_name = numeric_cols[0]
        ax2 = ax1.twinx()
        ax2.plot(comparison_df['year'], comparison_df[col_name], color='orange', marker='o', label=f'Avg {col_name.capitalize()}')
        ax2.set_ylabel(f"Average {col_name.capitalize()}", color='orange')

    plt.title("Flood vs Weather Trends (2014–2025)")
    fig.tight_layout()
    st.pyplot(fig)

    # --- Monthly Comparison ---
    if 'month' in flood_df.columns and 'month' in weather_df.columns:
        st.subheader("📅 Monthly Average Comparison per Year")

        for year in sorted(flood_df['year'].unique()):
            flood_monthly = flood_df[flood_df['year'] == year].groupby('month').size().reindex(
                ['January','February','March','April','May','June','July','August','September','October','November','December']
            ).fillna(0)

            if len(numeric_cols) > 0:
                weather_monthly = weather_df[weather_df['year'] == year].groupby('month')[numeric_cols[0]].mean().reindex(
                    ['January','February','March','April','May','June','July','August','September','October','November','December']
                ).fillna(0)

                fig, ax1 = plt.subplots(figsize=(10, 4))
                ax1.bar(flood_monthly.index, flood_monthly.values, color='skyblue', label='Floods')
                ax1.set_ylabel("Flood Occurrences", color='blue')
                ax1.set_xticklabels(flood_monthly.index, rotation=45, ha='right')

                ax2 = ax1.twinx()
                ax2.plot(weather_monthly.index, weather_monthly.values, color='orange', marker='o', label=f"Avg {numeric_cols[0].capitalize()}")
                ax2.set_ylabel(f"Avg {numeric_cols[0].capitalize()}", color='orange')

                plt.title(f"{year} Monthly Comparison")
                fig.tight_layout()
                st.pyplot(fig)

    # --- Summary ---
    st.subheader("🧾 Comparison Summary")
    st.write("""
    - The blue bars represent **flood occurrences** per year.
    - The orange line shows **average weather metrics** (e.g., rainfall or temperature).
    - Use these visuals to see patterns — like how increased rainfall affects flood frequency.
    """)

    st.dataframe(comparison_df)

else:
    st.info("⬆️ Upload both the Flood and Weather datasets to start the analysis.")
