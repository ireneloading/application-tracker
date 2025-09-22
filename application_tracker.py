import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---- Setup ----
st.set_page_config(page_title="Application Tracker", layout="wide")
st.title("📋 Application Tracker")

# ---- State ----
if "applications" not in st.session_state:
    st.session_state.applications = []

# ---- Input Form ----
st.header("➕ Add a New Application")
with st.form("application_form"):
    company = st.text_input("Company / Organization")
    role = st.text_input("Role / Opportunity Title")
    date_applied = st.date_input("Date Applied (optional)")
    status = st.selectbox("Status", ["Not Started", "Applied", "Interviewing", "Offer", "Rejected"])
    link = st.text_input("Link (optional)")
    notes = st.text_area("Notes / Next Steps")
    submit = st.form_submit_button("Add Entry")

    if submit and company and role:
        st.session_state.applications.append({
            "Company": company,
            "Role": role,
            "Date Applied": date_applied,
            "Status": status,
            "Link": link,
            "Notes": notes
        })
        st.success(f"✅ Added: {role} at {company}")

# ---- Display Table ----
if st.session_state.applications:
    df = pd.DataFrame(st.session_state.applications)

    st.header("📊 Application Overview")
    selected_status = st.multiselect("Filter by Status", df["Status"].unique(), default=list(df["Status"].unique()))
    sort_by = st.selectbox("Sort by", ["Company", "Role", "Date Applied"])

    filtered_df = df[df["Status"].isin(selected_status)].sort_values(by=sort_by)
    st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)

    # ---- Bar Chart ----
    st.subheader("📈 Number of Applications by Status")
    bar_data = df["Status"].value_counts().sort_index()
    fig1, ax1 = plt.subplots()
    ax1.bar(bar_data.index, bar_data.values)
    ax1.set_ylabel("Applications")
    st.pyplot(fig1)

    # ---- Pie Chart ----
    st.subheader("📊 Status Breakdown (Pie)")
    fig2, ax2 = plt.subplots()
    ax2.pie(bar_data.values, labels=bar_data.index, autopct="%1.1f%%", startangle=90)
    ax2.axis("equal")
    st.pyplot(fig2)

    # ---- Export ----
    st.subheader("📥 Download Your Data")
    csv = filtered_df.to_csv(index=False)
    st.download_button("Download CSV", csv, "application_tracker.csv", "text/csv")
else:
    st.info("Start by adding your first application above.")
