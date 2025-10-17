    # ------------------ Barangay Affected per Year ------------------
    st.subheader("🏘️ Barangay Affected per Year")

    # Detect barangay column automatically
    barangay_cols = [c for c in flood_df.columns if "barangay" in c.lower()]
    if barangay_cols:
        brgy_col = barangay_cols[0]

        # Group by year + barangay to count occurrences
        brgy_yearly = flood_df.groupby([year_col, brgy_col]).size().reset_index(name="flood_occurrences")

        # --- Graph per Year (only affected barangays) ---
        for year in sorted(brgy_yearly[year_col].unique()):
            yearly_brgy = brgy_yearly[brgy_yearly[year_col] == year]
            yearly_brgy = yearly_brgy[yearly_brgy["flood_occurrences"] > 0]  # show only affected

            if not yearly_brgy.empty:
                st.markdown(f"### 📅 {year} - Flood Occurrences per Barangay")
                fig, ax = plt.subplots(figsize=(9, 4))
                ax.bar(yearly_brgy[brgy_col], yearly_brgy["flood_occurrences"],
                       color="skyblue", edgecolor="black")
                ax.set_xlabel("Barangay")
                ax.set_ylabel("Flood Occurrences")
                ax.set_title(f"Flood-Affected Barangays - {year}")
                ax.set_xticklabels(yearly_brgy[brgy_col], rotation=45, ha="right")
                ax.grid(axis='y', linestyle='--', alpha=0.5)
                st.pyplot(fig)
            else:
                st.markdown(f"**{year}:** No barangays affected.")

        # --- Summary: Most Affected Barangays Overall ---
        st.markdown("### 📊 Summary: Most Affected Barangays (Overall)")

        total_impact = (
            brgy_yearly.groupby(brgy_col)["flood_occurrences"]
            .sum()
            .reset_index()
            .sort_values(by="flood_occurrences", ascending=False)
        )

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(total_impact[brgy_col], total_impact["flood_occurrences"],
               color="salmon", edgecolor="black")
        ax.set_xlabel("Barangay")
        ax.set_ylabel("Total Flood Occurrences")
        ax.set_title("Overall Flood Impact (Most Affected Barangays)")
        ax.set_xticklabels(total_impact[brgy_col], rotation=45, ha="right")
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        st.pyplot(fig)

        # --- List of Affected Barangays per Year ---
        st.markdown("### 📋 List of Affected Barangays per Year")
        year_groups = brgy_yearly.groupby(year_col)[brgy_col].unique().reset_index()
        for _, row in year_groups.iterrows():
            year = row[year_col]
            barangays = ", ".join(sorted(row[brgy_col]))
            st.markdown(f"**{year}:** {barangays}")
    else:
        st.warning("⚠️ No 'Barangay' column detected in flood dataset.")
