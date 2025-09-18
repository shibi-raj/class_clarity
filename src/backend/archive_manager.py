import os
import json
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any, Optional
from .gmail_client import fetch_teacher_emails
import datetime

ARCHIVE_ROOT = Path("data_archive")

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from a PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def archive_emails_for_day(teacher_emails: List[str], day: Optional[datetime.date] = None) -> List[Dict[str, Any]]:
    """Fetch emails from Gmail, save attachments, and archive as JSON with full_text."""
    if day is None:
        day = datetime.date.today()

    # 1. Fetch emails from Gmail
    emails = fetch_teacher_emails(teacher_emails, day=day)

    # 2. Prepare archive folder
    day_folder = ARCHIVE_ROOT / day.isoformat()
    attachments_folder = day_folder / "attachments"
    attachments_folder.mkdir(parents=True, exist_ok=True)
    
    archived_emails = []

    for email in emails:
        attachment_files = []

        # Save attachments (if any) and extract text
        for attachment in email.get("attachments", []):
            file_path = attachments_folder / attachment["filename"]
            with open(file_path, "wb") as f:
                f.write(attachment["data"])
            attachment_files.append(str(file_path))
        
        # Extract text from PDFs
        attachment_texts = ""
        for file_path in attachment_files:
            if file_path.lower().endswith(".pdf"):
                attachment_texts += extract_text_from_pdf(Path(file_path)) + "\n"

        # Merge email snippet + attachment text
        full_text = email.get("snippet", "") + "\n\n" + attachment_texts

        archived_email = {
            "from": email["from"],
            "subject": email["subject"],
            "date": email["date"],
            "attachments": attachment_files,
            "full_text": full_text
        }
        archived_emails.append(archived_email)

    # 3. Save archive JSON
    archive_json_path = day_folder / "archive.json"
    archive_data = {
        "processed": True,
        "emails": archived_emails
    }
    with open(archive_json_path, "w", encoding="utf-8") as f:
        json.dump(archive_data, f, ensure_ascii=False, indent=2)

    return archived_emails

def load_archived_emails(day: Optional[datetime.date] = None) -> Dict[str, Any]:
    """Load archived emails JSON for a given day."""
    if day is None:
        day = datetime.date.today()
    archive_json_path = ARCHIVE_ROOT / day.isoformat() / "archive.json"
    if not archive_json_path.exists():
        return {}
    with open(archive_json_path, "r", encoding="utf-8") as f:
        return json.load(f)