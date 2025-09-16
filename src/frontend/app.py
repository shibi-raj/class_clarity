import streamlit as st
import requests

st.title("Class_Clarity - Daily School Events")

# Fetch events from backend
response = requests.get("http://127.0.0.1:8000/get_events")
events = response.json().get("events", [])

# Display events in table
st.subheader("Prioritized Events")
st.table(events)

# TODO: Add calendar view