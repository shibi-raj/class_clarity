import streamlit as st
import requests
import yaml
from datetime import date
from pathlib import Path

# -------------------------------
# LOAD FRONTEND CONFIG
# -------------------------------
CONFIG_PATH = Path(__file__).parent / "config/config.yml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

BASE_URL = config.get("backend_url", "http://127.0.0.1:8000")
DEFAULT_USER_CONTEXT = config.get("default_user_context", "")
DEFAULT_START_DATE = config.get("default_start_date")
DEFAULT_END_DATE = config.get("default_end_date")

if DEFAULT_START_DATE is None:
    DEFAULT_START_DATE = date.today()
if DEFAULT_END_DATE is None:
    DEFAULT_END_DATE = date.today()

# -------------------------------
# STREAMLIT APP
# -------------------------------
st.set_page_config(page_title="Class Clarity", layout="wide")
st.title("Class Clarity - Student Events Dashboard")

# -------------------------------
# User Inputs
# -------------------------------
st.sidebar.header("User Preferences / Context")

user_context = st.sidebar.text_area(
    "Describe your interests for your child",
    value=DEFAULT_USER_CONTEXT
)

start_date = st.sidebar.date_input("Start Date", value=DEFAULT_START_DATE)
end_date = st.sidebar.date_input("End Date", value=DEFAULT_END_DATE)

if start_date > end_date:
    st.sidebar.error("Start date cannot be after end date.")

# -------------------------------
# Fetch Events Button
# -------------------------------
if st.sidebar.button("Fetch & Process Events"):
    with st.spinner("Fetching and processing events..."):
        try:
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "user_context": user_context
            }
            response = requests.get(f"{BASE_URL}/process_events", params=params)
            response.raise_for_status()
            data = response.json()

            st.header("Processed Events")
            
            # events = data.get("events", [])
            # if events:
            #     for evt in events:
            #         st.markdown(f"- **{evt.get('date', 'N/A')}**: {evt.get('event', '')}")
            # else:
            #     st.info("No events found in the selected date range.")

            st.header("LLM Output")
            llm_output = data.get("llm_output", "")
            if llm_output:
                st.text_area("Events & Summary", llm_output, height=400)
            else:
                st.info("No LLM output available for the selected date range.")

        except Exception as e:
            st.error(f"Error fetching events: {e}")