import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Read directly from the Google Sheet as CSV
sheet_url = "https://docs.google.com/spreadsheets/d/1sp5JyQiAJzw1bfgvR12FxT4icYi92goh/gviz/tq?tqx=out:csv"
df = pd.read_csv(sheet_url)

# Ensure the Date column is in datetime format and filter for future dates only
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df[df["Date"] >= pd.to_datetime("today")]

# Recreate the Slot column after filtering
df["Slot"] = df["Date"].dt.strftime("%Y-%m-%d") + " – " + df["Time"]

# Combine date and time into a slot column
df["Slot"] = df["Date"] + " – " + df["Time"]

# Custom styles to brighten the background and center the logo
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #f9f9ff;
    }

    img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        padding-bottom: 10px;
    }

    h1, .stMarkdown {
        color: #2c3e50;
    }

    section[aria-label="main"] {
        background-color: #ffffffdd;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- Load logo ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=200)

st.title("CareSync Virtual - Schedule a Telehealth Visit")

st.markdown("""
Welcome to **CareSync Virtual**   
You can use this tool to schedule a **telehealth visit** with a **palliative care physician or nurse practitioner**.  
Select your provider, visit type, choose a time slot, and confirm your appointment — it’s that easy.
""")

# --- Form Inputs ---
name = st.text_input("Patient Name")
email = st.text_input("Patient Email")
visit_type = st.radio("Visit Type", ["New Visit", "Follow-up Visit"])
provider_choice = st.selectbox("Choose a Provider", df["Provider"].unique())

# --- Filter based on visit type ---
if visit_type == "New Visit":
    duration_filter = df["Time"].str.contains("1:00") | df["Time"].str.contains("1hr|1 hr|1-hour", case=False)
else:
    time_filter = df["Time"].str.contains("30")

filtered_df = df[(df["Provider"] == provider_choice) & time_filter]
slot_choice = st.selectbox("Choose a Time Slot", filtered_df["Slot"].tolist())

# --- Book Appointment ---
if st.button("Confirm Appointment"):
    appointment = {
        "Patient Name": name,
        "Email": email,
        "Visit Type": visit_type,
        "Provider": provider_choice,
        "Slot": slot_choice,
        "Timestamp": datetime.now().isoformat()
    }

    # Save appointment to CSV
    appt_file = "appointments.csv"
    try:
        if os.path.exists(appt_file) and os.path.getsize(appt_file) > 0:
            appts = pd.read_csv(appt_file)
            appts = pd.concat([appts, pd.DataFrame([appointment])], ignore_index=True)
        else:
            appts = pd.DataFrame([appointment])
        appts.to_csv(appt_file, index=False)
        st.success(f"✅ Appointment booked for {name} ({visit_type}) with {provider_choice} at {slot_choice}.")
    except Exception as e:
        st.error(f"Error saving appointment: {e}")

# --- Admin download section ---
st.markdown("---")
st.subheader("🔐 Admin Access")

admin_pass = st.text_input("Enter admin password:", type="password")

if admin_pass == "oncadmin2024":
    st.success("Access granted. Download below:")
    if os.path.exists("appointments.csv"):
        with open("appointments.csv", "rb") as f:
            st.download_button(
                label="Download appointments.csv",
                data=f,
                file_name="appointments.csv",
                mime="text/csv"
            )
    else:
        st.info("No appointments have been booked yet.")
else:
    st.warning("Admin access only.")
