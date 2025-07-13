import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from sheets_utils import read_sheet_to_df, write_df_to_sheet

SHEET_NAME = "heartteam" 
PATIENTS_WS = "patients"
CONSULTS_WS = "consults"

# --- Load Data ---
try:
    st.session_state.patients = read_sheet_to_df(SHEET_NAME, PATIENTS_WS)
except Exception:
    st.session_state.patients = pd.DataFrame(columns=['HN', 'Name', 'Diagnosis', 'Ward', 'Bed'])

try:
    st.session_state.consults = read_sheet_to_df(SHEET_NAME, CONSULTS_WS)
except Exception:
    st.session_state.consults = pd.DataFrame(columns=['Consult_ID', 'HN', 'Consult from', 'Reason', 'Urgency', 'Time', 'Status'])

# --- UI ---
st.title("Heart team consultation")

# --- Section 1: Patient Panel ---
st.header("Patient identification")
with st.form("patient_form"):
    hn = st.text_input("HN")
    name = st.text_input("Patient Name")
    diagnosis = st.text_input("Diagnosis")
    submit_patient = st.form_submit_button("Add to Panel")

if submit_patient:
    new_patient = pd.DataFrame([{
        'HN': hn,
        'Name': name,
        'Diagnosis': diagnosis,
        'Ward': '',    # Add empty columns if needed
        'Bed': ''
    }])
    st.session_state.patients = pd.concat([st.session_state.patients, new_patient], ignore_index=True)
    write_df_to_sheet(st.session_state.patients, SHEET_NAME, PATIENTS_WS)
    st.success(f"Patient {hn} added to panel.")

# Display Patient Panel
st.subheader("Current Patient Panel")
st.dataframe(st.session_state.patients)

# --- Section 2: Consultation Request ---
st.header("🔹 Consultation Request")
with st.form("consult_form"):
    selected_hn = st.selectbox("Select Patient (HN)", st.session_state.patients['HN'] if not st.session_state.patients.empty else [])
    Consultfrom = st.selectbox("Consult from", ["Cardiology staff", "Surgeon",  "Others"])
    reason = st.text_area("Consultation Reason")
    urgency = st.radio("Urgency", ["Routine", "Urgent"])
    submit_consult = st.form_submit_button("Request Consult")

if submit_consult and selected_hn:
    new_consult = pd.DataFrame([{
        'Consult_ID': str(uuid.uuid4())[:8],
        'HN': selected_hn,
        'Consult from': Consultfrom,
        'Reason': reason,
        'Urgency': urgency,
        'Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Status': "Pending"
    }])
    st.session_state.consults = pd.concat([st.session_state.consults, new_consult], ignore_index=True)
    write_df_to_sheet(st.session_state.consults, SHEET_NAME, CONSULTS_WS)
    st.success(f"Consultation requested from {Consultfrom} for {selected_hn}.")


# --- Section 3: Consultation Queue Management ---
st.header("🔹 Consultation Queue Management")
st.dataframe(st.session_state.consults[['Consult_ID', 'HN', 'Consult from', 'Urgency', 'Time', 'Status']])

st.subheader("Update Consultation Status")
if not st.session_state.consults.empty:
    consult_to_update = st.selectbox("Select Consultation", st.session_state.consults['Consult_ID'])
    new_status = st.selectbox("New Status", ["Pending", "In Progress", "Answered", "Closed"])
    if st.button("Update Status"):
        idx = st.session_state.consults[st.session_state.consults['Consult_ID'] == consult_to_update].index[0]
        st.session_state.consults.at[idx, 'Status'] = new_status
        write_df_to_sheet(st.session_state.consults, SHEET_NAME, CONSULTS_WS)
        st.success(f"Consultation {consult_to_update} status updated to {new_status}")

# --- Optional Export ---
st.header("🔹 Export Data")
csv = st.session_state.consults.to_csv(index=False)
st.download_button("Download Consult Queue CSV", csv, file_name="consult_queue.csv", mime="text/csv")

