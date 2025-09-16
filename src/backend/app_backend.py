from fastapi import FastAPI
from src.backend.gmail_client import fetch_teacher_emails
from src.backend.llm_parser import parse_email_events

app = FastAPI()

@app.get("/get_events")
def get_events():
    emails = fetch_teacher_emails()
    events = parse_email_events(emails)
    return {"events": events}

# Run backend:
# uvicorn src.backend.app_backend:app --reload