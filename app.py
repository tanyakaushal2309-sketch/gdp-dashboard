import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
from datetime import datetime

st.set_page_config(layout="wide")

# -----------------------
# CONFIG
# -----------------------

WEIGHTS = {
    "PAN": 40,
    "Name": 30,
    "DOB": 25,
    "State": 15,
    "City": 10
}

# -----------------------
# SCORING FUNCTIONS
# -----------------------

def score_name(app_name, res_name):
    similarity = fuzz.token_sort_ratio(app_name, res_name)
    if similarity >= 95:
        return WEIGHTS["Name"]
    elif similarity >= 85:
        return 25
    elif similarity >= 70:
        return 15
    else:
        return 0

def score_dob(app_dob, res_dob):
    try:
        d1 = datetime.strptime(app_dob, "%d-%m-%Y")
        d2 = datetime.strptime(res_dob, "%d-%m-%Y")
        diff = abs((d1 - d2).days)

        if diff == 0:
            return WEIGHTS["DOB"]
        elif diff <= 30:
            return 20
        elif diff <= 90:
            return 15
        else:
            return 0
    except:
        return 0

def score_pan(app_pan, res_pan):
    return WEIGHTS["PAN"] if app_pan == res_pan and res_pan != "" else 0

def score_location(app_state, res_state, app_city, res_city):
    state_score = WEIGHTS["State"] if app_state == res_state else 0
    city_score = WEIGHTS["City"] if app_city == res_city else 0
    return state_score + city_score

def determine_status(score, crime):
    if score >= 90:
        status = "Confirmed"
    elif score >= 75:
        status = "High Probability"
    elif score >= 60:
        status = "Possible Match"
    else:
        status = "No Match"

    if crime == "High" and score >= 75:
        return "Escalate"

    return status

# -----------------------
# UI
# -----------------------

st.title("Savdhaan Intelligent Confidence Engine")

col1, col2 = st.columns(2)

with col1:
    app_name = st.text_input("Applicant Name", "Rahul Kumar Singh")
    app_dob = st.text_input("DOB (DD-MM-YYYY)", "10-05-1992")
    app_pan = st.text_input("PAN", "ABCDE1234F")

with col2:
    app_state = st.text_input("State", "Maharashtra")
    app_city = st.text_input("City", "Mumbai")

# Dummy multi-check data
crime_results = [
    {"name": "Rahul K Singh", "dob": "10-05-1992", "state": "Maharashtra", "city": "Mumbai", "pan": "", "severity": "Low", "link": "https://example.com/crime1"},
    {"name": "Rahul Kumar", "dob": "01-07-1991", "state": "MP", "city": "Indore", "pan": "", "severity": "High", "link": "https://example.com/crime2"}
]

political_results = [
    {"name": "R K Singh", "dob": "11-05-1992", "state": "Maharashtra", "city": "Mumbai", "pan": "", "severity": "Medium", "link": "https://example.com/political1"}
]

cibil_results = [
    {"name": "Rahul Kumar Singh", "dob": "10-05-1992", "state": "Maharashtra", "city": "Mumbai", "pan": "ABCDE1234F", "severity": "Low", "link": "https://example.com/cibil1"}
]

def process_results(results):
    processed = []
    for r in results:
        pan_s = score_pan(app_pan, r["pan"])
        name_s = score_name(app_name, r["name"])
        dob_s = score_dob(app_dob, r["dob"])
        loc_s = score_location(app_state, r["state"], app_city, r["city"])

        total = pan_s + name_s + dob_s + loc_s
        status = determine_status(total, r["severity"])

        breakdown = {
            "PAN Score": pan_s,
            "Name Score": name_s,
            "DOB Score": dob_s,
            "Location Score": loc_s
        }

        processed.append((r, total, status, breakdown))

    return processed

if st.button("Run Savdhaan Check"):

    tab1, tab2, tab3 = st.tabs(["Crime Check", "Political Check", "CIBIL Check"])

    for tab, data in zip([tab1, tab2, tab3],
                         [crime_results, political_results, cibil_results]):

        with tab:
            results = process_results(data)

            for r, score, status, breakdown in results:
                st.markdown(f"### {r['name']}")
                st.write(f"Confidence Score: **{score}**")
                st.write(f"Status: **{status}**")
                st.write(f"[View Source Link]({r['link']})")

                with st.expander("See Scoring Logic Breakdown"):
                    st.json(breakdown)

    st.success("All checks processed successfully.")
