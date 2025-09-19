from typing import List, Dict, Any, Optional
import re
from dateutil.parser import parse as parse_date


# ...  Handles Ollama parsing
def parse_email_events(emails):
    # TODO: send each email body to Ollama
    # Example JSON output:
    return [
        {"event": "Math Test", "date": "2025-09-18", "time": "10:00", "priority": "High"}
    ]


# User context (interests)
USER_CONTEXT = """
I want my child to be well-rounded and excel in academics and sports.
Provide deadlines, test dates, and special academic/sports events, try-out dates, concerts, etc.
"""

# Output context (format instructions)
OUTPUT_CONTEXT = """
Return a bulleted, prioritized list of events with relevant dates.
Include calendar-ready entries where possible.
"""


DATE_PATTERNS = [
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b",
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b"
    ]

def generate_llm_prompt(
    archived_emails: List[Dict[str, Any]],
    user_context: str = USER_CONTEXT, 
    output_context: str = OUTPUT_CONTEXT
) -> str:
    email_texts = [email.get("full_text", "") for email in archived_emails]
    emails_combined = "\n\n".join(email_texts)

    prompt = (
        f"USER CONTEXT:\n{user_context}\n\n"
        f"OUTPUT CONTEXT:\n{output_context}\n\n"
        f"EMAIL CONTENT:\n{emails_combined}"
    )
    return prompt.strip()


def extract_events_with_dates(llm_text: str):
    results = []
    lines = llm_text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        for pattern in DATE_PATTERNS:
            match = re.search(pattern, line)
            if match:
                date_str = match.group(0)
                # Normalize date to YYYY-MM-DD
                try:
                    normalized_date = parse_date(date_str).date().isoformat()
                except Exception:
                    normalized_date = date_str
                results.append({
                    "event": line,
                    "date": normalized_date,
                    "notes": ""
                })
                break  # Stop after first date found in line
    return results