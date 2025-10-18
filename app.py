# ==========================================================
# 🌊 Flood Pattern Data Mining & Forecasting System
# ==========================================================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, mean_absolute_error
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller

# ----------------------------------------------------------
# Page setup
# ----------------------------------------------------------
st.set_page_config(page_title="Flood Pattern Analysis System", layout="wide", page_icon="🌊")
st.title("🌊 Flood Pattern Data Mining and Prediction System")

# ==========================================================
# 1️⃣ Data Upload and Overview
# ==========================================================
st.header("📂 1. Upload and Explore Data")

uploaded = st.file_uploader("Upload your flood dataset (CSV format)", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)
    st.session_state.df = df
    st.success("✅ File uploaded successfully!")

    st.write("**Dataset Shape:**", df.shape)
    st.write("**Data Types:**")
    st.write(df.dtypes)
    st.dataframe(df.head())

    st.write("**Missing Values:**")
    st.write(df.isnull().sum())
else:
    st.info("Please upload a CSV file to begin.")
    st.stop()

# ==========================================================
# 2️⃣ Data Cleaning and Visualization
# ==========================================================
st.header("🧹 2. Data Cleaning and Visualization")

df["Water Level"] = (
    df["Water Level"].astype(str)
    .str.replace("ft", "")
    .str.replace(" ", "")
    .replace("nan", np.nan)
)
df["Water Level"] = pd.to_numeric(df["Water Level"], errors="coerce")
df["Water Level"].fillna(df["Water Level"].median(), inplace=True)

fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(df["Water Level"], bins=20, edgecolor="black", color="skyblue")
ax.set_title("Distribution of Water Level")
st.pyplot(fig)

# ==========================================================
# 3️⃣ Clustering and Pattern Discovery
# ==========================================================
st.header("🔍 3. Flood Pattern Clustering (K-Means)")

cluster_cols = ["Water Level", "No. of Families affected", "Damage Infrastructure", "Damage Agriculture"]
X = df[cluster_cols].fillna(0)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df["Cluster"] = kmeans.fit_predict(X)
st.write("**Cluster Counts:**")
st.bar_chart(df["Cluster"].value_counts())

fig, ax = plt.subplots()
ax.scatter(df["Water Level"], df["Damage Infrastructure"], c=df["Cluster"], cmap="viridis")
ax.set_xlabel("Water Level")
ax.set_ylabel("Damage Infrastructure")
ax.set_title("Cluster Visualization")
st.pyplot(fig)

# ==========================================================
# 4️⃣ Flood Occurrence Prediction (Random Forest)
# ==========================================================
st.header("🤖 4. Flood Occurrence Prediction")

df["flood_occurred"] = (df["Water Level"] > 0).astype(int)

if "Month" in df.columns:
    df["Month"] = df["Month"].fillna("Unknown")
    month_dummies = pd.get_dummies(df["Month"], prefix="Month")
    df = pd.concat([df, month_dummies], axis=1)
else:
    st.warning("⚠️ 'Month' column missing; skipping month-based features.")
    month_dummies = pd.DataFrame()

features = ["Water Level", "No. of Families affected", "Damage Infrastructure", "Damage Agriculture"] + list(month_dummies.columns)
X = df[features]
y = df["flood_occurred"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
rf = RandomForestClassifier(random_state=42)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)

st.metric("Model Accuracy", f"{accuracy_score(y_test, y_pred):.2%}")
st.text("Classification Report:")
st.text(classification_report(y_test, y_pred))

# Monthly flood probability
if "Month" in df.columns:
    monthly_flood = df.groupby("Month")["flood_occurred"].mean().sort_values(ascending=False)
    st.subheader("📅 Monthly Flood Probability")
    fig2, ax2 = plt.subplots()
    monthly_flood.plot(kind="bar", ax=ax2, color="skyblue")
    ax2.set_ylabel("Flood Probability")
    st.pyplot(fig2)

# ==========================================================
# 5️⃣ SARIMA Time-Series Forecasting
# ==========================================================
st.header("📈 5. SARIMA Water Level Forecasting")

if all(col in df.columns for col in ["Year", "Month", "Day"]):
    # Create datetime
    month_map = {"JANUARY":1,"FEBRUARY":2,"MARCH":3,"APRIL":4,"MAY":5,"JUNE":6,
                 "JULY":7,"AUGUST":8,"SEPTEMBER":9,"OCTOBER":10,"NOVEMBER":11,"DECEMBER":12,"Unknown":1}
    df["Month_Num"] = df["Month"].map(month_map)
    df["Year"] = df["Year"].fillna(method="ffill").astype(int)
    df["Day"] = df["Day"].fillna(method="ffill").astype(int)
    temp = df[["Year","Month_Num","Day"]].rename(columns={"Month_Num":"month"})
    df["Date"] = pd.to_datetime(temp, errors="coerce")
    df = df.set_index("Date")
    ts = df["Water Level"].resample("D").mean().fillna(method="ffill").fillna(method="bfill")

    st.line_chart(ts, use_container_width=True)

    adf = adfuller(ts.dropna())
    st.write(f"ADF Statistic: {adf[0]:.4f}, p-value: {adf[1]:.4f}")

    p = st.number_input("p", 0, 5, 1)
    d = st.number_input("d", 0, 2, 1)
    q = st.number_input("q", 0, 5, 1)
    s = st.number_input("Seasonal period (s)", 1, 365, 7)
    steps = st.slider("Days to forecast ahead", 7, 90, 30)

    if st.button("🚀 Train SARIMA Model"):
        try:
            model = SARIMAX(ts, order=(p, d, q), seasonal_order=(1, 0, 1, s))
            results = model.fit(disp=False)
            future_dates = pd.date_range(ts.index[-1] + pd.Timedelta(days=1), periods=steps, freq="D")
            forecast = results.predict(start=future_dates[0], end=future_dates[-1])

            fig3, ax3 = plt.subplots(figsize=(10, 5))
            ax3.plot(ts, label="Historical")
            ax3.plot(forecast, color="red", label="Forecast")
            ax3.legend()
            ax3.set_title("SARIMA Forecast of Daily Average Water Level")
            st.pyplot(fig3)

            fitted = results.fittedvalues
            rmse = np.sqrt(mean_squared_error(ts.loc[fitted.index], fitted))
            mae = mean_absolute_error(ts.loc[fitted.index], fitted)
            st.metric("RMSE", f"{rmse:.4f}")
            st.metric("MAE", f"{mae:.4f}")
        except Exception as e:
            st.error(f"Model training failed: {e}")
else:
    st.info("⏳ SARIMA requires Year, Month, and Day columns to create a date index.")

# ==========================================================
# 6️⃣ Insights and Recommendations
# ==========================================================
st.header("📊 6. Insights and Recommendations Dashboard")

if "flood_occurred" in df.columns and "Month" in df.columns:
    st.subheader("🌧️ Flood Occurrence by Month")
    monthly = df.groupby("Month")["flood_occurred"].mean().sort_values(ascending=False)
    st.bar_chart(monthly)
    st.write("Top 3 flood-prone months:")
    st.dataframe(monthly.head(3))

if "Barangay" in df.columns:
    st.subheader("🏘️ Most Affected Barangays")
    brgy = df.groupby("Barangay")["Water Level"].mean().sort_values(ascending=False)
    st.bar_chart(brgy.head(10))

if "Flood Cause" in df.columns:
    st.subheader("⚠️ Common Flood Causes")
    causes = df["Flood Cause"].value_counts()
    st.plotly_chart(px.pie(values=causes.values, names=causes.index, title="Flood Causes Distribution"))

if "Cluster" in df.columns:
    st.subheader("🧩 Cluster Summary")
    st.dataframe(df.groupby("Cluster")[["Water Level", "Damage Infrastructure", "Damage Agriculture"]].mean().round(2))

st.markdown("""
---
### 🧠 **Key Takeaways**
- **Peak Flood Season:** December to February  
- **Top Flood-Prone Barangays:** Poblacion, Imelda, Bunawan Brook  
- **Main Causes:** Low Pressure Area (LPA), Easterlies, Shearline  
- **Cluster Insights:**  
  - Cluster 0 → Frequent low-impact floods  
  - Cluster 1 → Moderate with agricultural damage  
  - Cluster 2 → Severe infrastructure damage  

---
### 🛠 **Recommendations**
- Strengthen flood defenses in top barangays  
- Develop early warning systems based on LPA and Shearline alerts  
- Support flood-resilient crops in agricultural areas  
- Improve data recording for better model accuracy  
""")

st.success("✅ Analysis complete! Explore results and plan accordingly.")
