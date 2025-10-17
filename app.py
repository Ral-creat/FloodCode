    # ------------------ Barangay Affected per Year (Fixed for Missing Barangays) ------------------
    st.subheader("🏘️ Barangay Affected per Year (Complete)")

    # Detect barangay column automatically
    barangay_cols = [c for c in flood_df.columns if "barangay" in c.lower()]
    if barangay_cols:
        brgy_col = barangay_cols[0]

        # Ensure barangay names are cleaned properly
        flood_df[brgy_col] = flood_df[brgy_col].astype(str).str.strip().str.title()

        # Get all barangays and all years
        all_barangays = sorted(flood_df[brgy_col].dropna().unique())
        all_years = sorted(flood_df[year_col].dropna().unique())

        # Create a full grid (every barangay × every year)
        full_combo = pd.MultiIndex.from_product(
            [all_years, all_barangays],
            names=[year_col, brgy_col]
        ).to_frame(index=False)

        # Actual flood occurrences
        brgy_yearly = (
            flood_df.groupby([year_col, brgy_col])
            .size()
            .reset_index(name="flood_occurrences")
        )

        # Merge full combo to include missing barangays (fill zeros)
        brgy_yearly = pd.merge(full_combo, brgy_yearly, on=[year_col, brgy_col], how="left").fillna(0)
        brgy_yearly["flood_occurrences"] = brgy_yearly["flood_occurrences"].astype(int)

        # ---- Yearly Graphs ----
        for year in all_years:
            yearly_data = brgy_yearly[brgy_yearly[year_col] == year]
            st.markdown(f"### 📅 {year} - Flood Occurrences per Barangay")

            fig, ax = plt.subplots(figsize=(10, 4))
            ax.bar(yearly_data[brgy_col], yearly_data["flood_occurrences"],
                   color="lightcoral", edgecolor="black")
            ax.set_xlabel("Barangay")
            ax.set_ylabel("Flood Occurrences")
            ax.set_title(f"Flood Occurrences by Barangay - {year}")
            ax.set_xticklabels(yearly_data[brgy_col], rotation=45, ha="right")
            ax.grid(axis="y", linestyle="--", alpha=0.5)
            st.pyplot(fig)

        # ---- List of Barangays per Year ----
        st.markdown("### 📋 List of Barangays Affected per Year")
        year_groups = (
            brgy_yearly[brgy_yearly["flood_occurrences"] > 0]
            .groupby(year_col)[brgy_col]
            .apply(lambda x: ", ".join(sorted(set(x))))
            .reset_index()
        )
        for _, row in year_groups.iterrows():
            st.markdown(f"**{row[year_col]}:** {row[brgy_col]}")

        # ---- Summary: Most Affected Barangays ----
        st.subheader("🔥 Summary: Most Frequently Flooded Barangays (2014–2025)")

        brgy_summary = (
            brgy_yearly.groupby(brgy_col)["flood_occurrences"]
            .sum()
            .reset_index()
            .sort_values("flood_occurrences", ascending=False)
        )

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(brgy_summary[brgy_col], brgy_summary["flood_occurrences"],
               color="tomato", edgecolor="black")
        ax.set_xlabel("Barangay")
        ax.set_ylabel("Total Flood Occurrences (2014–2025)")
        ax.set_title("Total Flood Occurrences by Barangay (All Years)")
        ax.set_xticklabels(brgy_summary[brgy_col], rotation=45, ha="right")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        st.pyplot(fig)

        st.dataframe(brgy_summary)

    else:
        st.warning("⚠️ No 'Barangay' column detected in the flood dataset.")
