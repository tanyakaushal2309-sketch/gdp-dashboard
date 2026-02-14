import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
from datetime import datetime

# ---------------------------
# CONFIG
# ---------------------------
WEIGHTS = {
    "pan": 40,
    "name": 30,
    "dob": 25,
    "state": 15,
    "city": 10
}

# ---------------------------
# FUNCTIONS
# ---------------------------

def calculate_name_score(applicant_name, result_name):
    similarity = fuzz.token_sort_ratio(applicant_name, result_name)
    if similarity >= 95:
        return 30
    elif similarity >= 85:
        return 25
    elif similarity >= 70:
        return 15
    else:
        return 0

def calculate_dob_score(applicant_dob, result_dob):
    try:
        d1 = datetime.strptime(applicant_dob, "%d-%m-%Y")
        d2 = datetime.strptime(result_dob, "%d-%m-%Y")
        diff = abs((d1 - d2).days)

        if diff == 0:
            return 25
        elif diff <= 30:
            return 20
        elif diff <= 90:
            return 15
        else:
            return 0
    except:
        return 0

def calculate_pan_score(applicant_pan, result_pan):
    if applicant_pan and result_pan and applicant_pan == result_pan:
        return 40
    return 0

def calculate_location_score(applicant_state, result_state,
                             applicant_city, result_city):
    state_score = 15 if applicant_state == result_state else 0
    city_score = 10 if applicant_city == result_city else 0
    return state_score + city_score

def determine_status(score, crime_severity):
    if score >= 90:
        status = "Confirmed Match"
    elif score >= 75:
        status = "High Probability"
    elif score >= 60:
        status = "Possible Match"
    else:
        status = "No Match"

    if crime_severity == "High" and score >= 75:
        return "Escalate"

    return status

# ---------------------------
# STREAMLIT UI
# ---------------------------

st.title("Savdhaan Confidence Scoring Engine")

st.header("Applicant Details")

applicant_name = st.text_input("Name", "Rahul Kumar Singh")
applicant_dob = st.text_input("DOB (DD-MM-YYYY)", "10-05-1992")
applicant_pan = st.text_input("PAN", "ABCDE1234F")
applicant_state = st.text_input("State", "Maharashtra")
applicant_city = st.text_input("City", "Mumbai")

# Dummy Savdhaan Results
results = [
    {"name": "Rahul K Singh", "dob": "10-05-1992", "state": "Maharashtra", "city": "Mumbai", "pan": "", "crime": "Low"},
    {"name": "Rahul Kumar", "dob": "01-07-1991", "state": "MP", "city": "Indore", "pan": "", "crime": "High"},
    {"name": "R K Singh", "dob": "11-05-1992", "state": "Maharashtra", "city": "Mumbai", "pan": "", "crime": "Medium"},
    {"name": "Rahul Kumar Singh", "dob": "10-05-1992", "state": "Maharashtra", "city": "Mumbai", "pan": "ABCDE1234F", "crime": "Low"},
]

if st.button("Run Savdhaan Check"):

    final_data = []

    for r in results:
        score = 0
        score += calculate_pan_score(applicant_pan, r["pan"])
        score += calculate_name_score(applicant_name, r["name"])
        score += calculate_dob_score(applicant_dob, r["dob"])
        score += calculate_location_score(applicant_state, r["state"],
                                          applicant_city, r["city"])

        status = determine_status(score, r["crime"])

        final_data.append({
            "Result Name": r["name"],
            "Crime Severity": r["crime"],
            "Confidence Score": score,
            "Status": status
        })

    df = pd.DataFrame(final_data)

    st.subheader("Results")
    st.dataframe(df)

    st.success("Scoring Completed Successfully")
