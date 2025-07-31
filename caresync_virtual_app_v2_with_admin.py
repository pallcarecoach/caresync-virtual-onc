
import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.message import EmailMessage
import os

# Load slot data from CSV (you'll replace this with your real data source)
slots_file = "open_slots.csv"
if not os.path.exists(slots_file):
    sample_data = [
        {"Provider": "Jane Smith", "Date": "2025-08-04", "Time": "10:00 - 10:30"},
        {"Provider": "Sandhya Mudumbi", "Date": "2025-08-01", "Time": "2:00 - 2:30"},
        {"Provider": "Avi B", "Date": "2025-08-07", "Time": "10:00 - 10:30"},
        {"Provider": "Xaden R", "Date": "2025-08-06", "Time": "1:00 - 2:00"},
    ]
    pd.DataFrame(sample_data).to_csv(slots_file, index=False)

df = pd.read_csv(slots_file)
df["Slot"] = df["Date"] + " – " + df["Time"]

st.title("CareSync Virtual - Schedule a Telehealth Visit")

name = st.text_input("Patient Name")
email = st.text_input("Patient Email")
provider_choice = st.selectbox("Choose a Provider", df["Provider"].unique())

available_slots = df[df["Provider"] == provider_choice]["Slot"].tolist()
slot_choice = st.selectbox("Choose a Time Slot", available_slots)

if st.button("Confirm Appointment"):
    appointment = {
        "Patient Name": name,
        "Email": email,
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

    # Placeholder for email confirmation
    st.success(f"✅ Appointment booked for {name} with {provider_choice} at {slot_choice}. Confirmation would be sent to {email}.")



# 🔐 Admin-only download access
st.markdown("---")
st.subheader("🔐 Admin Access")

admin_pass = st.text_input("Enter admin password:", type="password")

if admin_pass == "oncadmin2024":  # 🔐 Secure password
    st.success("Access granted. Download below:")
    appt_file = "appointments.csv"
    if os.path.exists(appt_file):
        with open(appt_file, "rb") as f:
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
