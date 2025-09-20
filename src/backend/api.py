from fastapi import FastAPI, Query
from typing import Optional
import datetime
import yaml
from pathlib import Path
from ollama import chat

from src.backend.archive_manager import load_email_window
from src.backend.llm_processor import (
    generate_llm_prompt,
    # extract_events_with_dates,
    USER_CONTEXT,
    OUTPUT_CONTEXT,
)

# Run backend:
# uvicorn src.backend.app_backend:app --reload


app = FastAPI()

# -------------------------------
# Load LLM config
# -------------------------------
CONFIG_PATH = Path("src/backend/config/llm_config.yml")
with open(CONFIG_PATH, "r") as f:
    llm_config = yaml.safe_load(f)

MODEL_NAME = llm_config.get("model", "llama3")  # fallback default


# -------------------------------
# Endpoint: processed events
# -------------------------------
@app.get("/process_events")
def process_events(
    start_date: datetime.date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="End date (YYYY-MM-DD, defaults to today+1)")
):
    try:
        # Load email archive window
        print("start end: ", start_date, end_date)
        archive_data = load_email_window(start_date, end_date)

        emails = archive_data.get("emails", [])
        if not emails:
            return {"message": "No emails found for given range."}

        # Generate prompt
        prompt = generate_llm_prompt(
            emails,
            user_context=USER_CONTEXT,
            output_context=OUTPUT_CONTEXT
        )

        # Call Ollama
        response = chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        llm_output = response["message"]["content"]

        # Extract structured events
        # extracted_events = extract_events_with_dates(llm_output)

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat() if end_date else None,
            "num_emails": len(emails),
            "llm_output": llm_output,
            # "extracted_events": extracted_events,
        }

    except Exception as e:
        return {"error": str(e)}