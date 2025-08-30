import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# --- Setup ---
st.set_page_config(page_title="📋 Application Tracker 2.0", layout="wide")
st.title("📋 Application Tracker 2.0")

DATA_FILE = "applications_data.csv"

# --- Load Data ---
try:
    df = pd.read_csv(DATA_FILE, parse_dates=["Date Applied", "Reminder Date"])
except FileNotFoundError:
    df = pd.DataFrame(columns=["Company", "Role", "Date Applied", "Status", "Link", "Notes", "Reminder Date"])

# --- Input Form ---
st.header("➕ Add a New Application")
with st.form("application_form"):
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("Company / Organization")
        role = st.text_input("Role / Opportunity Title")
    with col2:
        date_applied = st.date_input("Date Applied", value=datetime.today())
        add_reminder = st.checkbox("Set follow-up reminder for 7 days later")
    status = st.selectbox("Status", ["Not Started", "Applied", "Interviewing", "Offer", "Rejected"])
    link = st.text_input("Link (optional)")
    notes = st.text_area("Notes / Next Steps")
    submit = st.form_submit_button("Add Entry")

    if submit and company and role:
        reminder_date = date_applied + timedelta(days=7) if add_reminder else pd.NaT
        new_row = pd.DataFrame([{
            "Company": company,
            "Role": role,
            "Date Applied": pd.to_datetime(date_applied),
            "Status": status,
            "Link": link,
            "Notes": notes,
            "Reminder Date": reminder_date
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success(f"✅ Added: {role} at {company}")

# --- Weekly Goal Tracker ---
st.header("🎯 Weekly Goal Tracker")
goal = st.number_input("Set your weekly application goal:", min_value=1, max_value=50, value=5)
this_week = pd.Timestamp.today().normalize() - pd.to_timedelta(pd.Timestamp.today().weekday(), unit='d')
weekly_count = df[df["Date Applied"] >= this_week].shape[0]
st.progress(min(weekly_count / goal, 1.0))
st.caption(f"Applied {weekly_count} / {goal} jobs this week.")

# --- Display Table ---
if not df.empty:
    st.header("📊 Application Overview")
    selected_status = st.multiselect("Filter by Status", df["Status"].unique(), default=list(df["Status"].unique()))
    sort_by = st.selectbox("Sort by", ["Company", "Role", "Date Applied"])
    filtered_df = df[df["Status"].isin(selected_status)].sort_values(by=sort_by)
    st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)

    # --- Bar Chart ---
    st.subheader("📈 Applications by Status")
    bar_data = df["Status"].value_counts().sort_index()
    fig1, ax1 = plt.subplots()
    ax1.bar(bar_data.index, bar_data.values)
    ax1.set_ylabel("Applications")
    st.pyplot(fig1)

    # --- Pie Chart ---
    st.subheader("📊 Status Breakdown (Pie)")
    fig2, ax2 = plt.subplots()
    ax2.pie(bar_data.values, labels=bar_data.index, autopct="%1.1f%%", startangle=90)
    ax2.axis("equal")
    st.pyplot(fig2)

    # --- Line Graph: Weekly Trend ---
    st.subheader("📈 Weekly Application Trend")
    df["Week"] = df["Date Applied"].dt.to_period("W").astype(str)
    weekly_trend = df.groupby("Week").size()
    fig3, ax3 = plt.subplots()
    weekly_trend.plot(ax=ax3, marker='o')
    ax3.set_ylabel("Applications per Week")
    ax3.set_xlabel("Week")
    ax3.set_title("Trend Over Time")
    st.pyplot(fig3)

    # --- Calendar View ---
    st.subheader("🗓️ Application Calendar View")
    st.dataframe(df.sort_values("Date Applied")[["Company", "Role", "Date Applied"]], use_container_width=True)

    # --- Follow-up Reminders ---
    st.subheader("🔔 Follow-up Reminders")
    today = pd.Timestamp.today().normalize()
    reminders_due = df[df["Reminder Date"] == today]
    if not reminders_due.empty:
        st.warning("🔔 You have follow-ups due today:")
        st.dataframe(reminders_due[["Company", "Role", "Reminder Date"]])
    else:
        st.info("🎉 No follow-ups due today.")

    # --- Export Data ---
    st.subheader("📥 Download Your Data")
    csv = filtered_df.to_csv(index=False)
    st.download_button("Download CSV", csv, "application_tracker.csv", "text/csv")
else:
    st.info("Start by adding your first application above.")
