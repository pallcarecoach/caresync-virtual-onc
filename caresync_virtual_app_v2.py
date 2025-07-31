
<style>
/* Brighter, cleaner background */
[data-testid="stAppViewContainer"] {
    background-color: #f9f9ff;
}

/* Logo styling */
img {
    display: block;
    margin-left: auto;
    margin-right: auto;
    padding-bottom: 10px;
}

/* Main content text formatting */
h1, .stMarkdown {
    color: #2c3e50;
}

/* Admin section formatting */
section[aria-label="main"] {
    background-color: #ffffffdd;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.05);
}
</style>


import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Load logo ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=200)

st.title("CareSync Virtual - Schedule a Telehealth Visit")

st.markdown("""
Welcome to **CareSync Virtual** 👩‍⚕️👨‍⚕️  
You can use this tool to schedule a **telehealth visit** with a **palliative care physician or nurse practitioner**.  
Select your provider, visit type, choose a time slot, and confirm your appointment — it’s that easy.
""")

# --- Load slot data ---
slots_file = "open_slots.csv"
if not os.path.exists(slots_file):
    sample_data = [
        {"Provider": "Jane Smith", "Date": "2025-08-04", "Time": "10:00 - 10:30"},
        {"Provider": "Sandhya Mudumbi", "Date": "2025-08-01", "Time": "2:00 - 3:00"},
        {"Provider": "Avi B", "Date": "2025-08-07", "Time": "10:00 - 10:30"},
        {"Provider": "Xaden R", "Date": "2025-08-06", "Time": "1:00 - 2:00"},
    ]
    pd.DataFrame(sample_data).to_csv(slots_file, index=False)

df = pd.read_csv(slots_file)
df["Slot"] = df["Date"] + " – " + df["Time"]

# --- Form Inputs ---
name = st.text_input("Patient Name")
email = st.text_input("Patient Email")
visit_type = st.radio("Visit Type", ["New Visit", "Follow-up Visit"])
provider_choice = st.selectbox("Choose a Provider", df["Provider"].unique())

# --- Filter based on visit type ---
if visit_type == "New Visit":
    time_filter = df["Time"].str.contains("1:00") | df["Time"].str.contains("1 hour")
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
    if os.path.exists(appt_file):
        appts = pd.read_csv(appt_file)
        appts = appts.append(appointment, ignore_index=True)
    else:
        appts = pd.DataFrame([appointment])
    appts.to_csv(appt_file, index=False)

    st.success(f"✅ Appointment booked for {name} ({visit_type}) with {provider_choice} at {slot_choice}.")

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
