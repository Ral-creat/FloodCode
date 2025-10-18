# app.py
"""
Flood & Weather Data Analysis Streamlit App
- Upload CSV/XLSX data
- Handles UnicodeDecodeError
- Displays data characteristics & summaries
- Suggests preprocessing steps
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Flood & Weather Data Analyzer", layout="wide")

# ------------------ FILE UPLOAD ------------------
st.title("🌊 Flood & Weather Data Analysis App")

uploaded = st.file_uploader("📂 Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded:
    try:
        # Detect file type
        if uploaded.name.endswith(".csv"):
            try:
                df = pd.read_csv(uploaded, encoding="utf-8")
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(uploaded, encoding="latin1")
                except Exception as e:
                    st.error(f"❌ Error reading file: {e}")
                    st.stop()
        else:
            df = pd.read_excel(uploaded)

        st.success("✅ File uploaded successfully!")

        # ------------------ DATA DISPLAY ------------------
        st.subheader("📋 Data Preview")
        st.dataframe(df.head())

        st.subheader("📊 Dataset Information")
        st.write(f"**Rows:** {df.shape[0]} | **Columns:** {df.shape[1]}")

        st.write("**Column Names:**", list(df.columns))

        st.subheader("📈 Basic Statistics")
        st.write(df.describe(include='all'))

        # ------------------ DATA ANALYSIS ------------------
        st.subheader("🧹 Suggested Preprocessing Steps")

        suggestions = []

        # Missing values
        missing = df.isnull().sum()
        if missing.any():
            suggestions.append("🔹 Handle missing values (fill, drop, or impute).")

        # Duplicates
        if df.duplicated().any():
            suggestions.append("🔹 Remove duplicate rows to avoid bias.")

        # Datetime conversion
        datetime_cols = [c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()]
        if datetime_cols:
            suggestions.append(f"🔹 Convert {datetime_cols} to datetime format.")

        # Encoding text columns
        object_cols = df.select_dtypes(include=['object']).columns.tolist()
        if len(object_cols) > 0:
            suggestions.append("🔹 Encode categorical/text columns for ML models.")

        # Scaling numeric data
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(num_cols) > 0:
            suggestions.append("🔹 Normalize or standardize numerical columns.")

        if suggestions:
            for s in suggestions:
                st.markdown(s)
        else:
            st.info("✅ Data looks clean and ready for analysis!")

        # ------------------ VISUALIZATION ------------------
        st.subheader("📉 Quick Visualizations")
        numeric_cols = df.select_dtypes(include=np.number).columns

        if len(numeric_cols) > 0:
            selected_col = st.selectbox("Select a numeric column to visualize:", numeric_cols)
            fig, ax = plt.subplots()
            df[selected_col].hist(bins=20, ax=ax)
            ax.set_title(f"Distribution of {selected_col}")
            ax.set_xlabel(selected_col)
            ax.set_ylabel("Frequency")
            st.pyplot(fig)
        else:
            st.warning("No numeric columns available for visualization.")

    except Exception as e:
        st.error(f"⚠️ Failed to process file: {e}")
else:
    st.info("⬆️ Upload a CSV or Excel file to start the analysis.")
