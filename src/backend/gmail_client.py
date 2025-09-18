import os
import datetime
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import BatchHttpRequest
from typing import List, Dict, Any, Optional
from zoneinfo import ZoneInfo

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    creds = None
    token_path = os.path.join("creds", "token.json")
    creds_path = os.path.join("creds", "credentials.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service

def get_utc_bounds_for_local_day(local_day: datetime.date, tz_name: str = "America/New_York"):
    tz = ZoneInfo(tz_name)
    local_start = datetime.datetime.combine(local_day, datetime.time.min, tzinfo=tz)
    local_end = datetime.datetime.combine(local_day + datetime.timedelta(days=1), datetime.time.min, tzinfo=tz)

    utc_start = local_start.astimezone(ZoneInfo("UTC"))
    utc_end = local_end.astimezone(ZoneInfo("UTC"))

    after_str = utc_start.strftime("%Y/%m/%d")
    before_str = utc_end.strftime("%Y/%m/%d")
    return after_str, before_str

def decode_base64(data: str) -> str:
    return base64.urlsafe_b64decode(data.encode("UTF-8")).decode("UTF-8", errors="ignore")

def extract_text_from_payload(payload: Dict[str, Any]) -> str:
    """Recursively extract text from all parts."""
    if "parts" in payload:
        text = ""
        for part in payload["parts"]:
            text += extract_text_from_payload(part)
        return text
    if payload.get("mimeType") == "text/plain" and "data" in payload.get("body", {}):
        return decode_base64(payload["body"]["data"])
    return ""

def fetch_teacher_emails(
    teacher_emails: List[str],
    day: Optional[datetime.date] = None
) -> List[Dict[str, Any]]:
    service = authenticate_gmail()
    if day is None:
        day = datetime.date.today()

    after_str, before_str = get_utc_bounds_for_local_day(day)

    teachers_query = " OR ".join([f"from:{t}" for t in teacher_emails])
    query = f"({teachers_query}) after:{after_str} before:{before_str}"
    print("DEBUG QUERY:", query)

    response = service.users().messages().list(userId="me", q=query).execute()
    messages = response.get("messages", [])

    results: List[Dict[str, Any]] = []

    def callback(request_id, response, exception):
        if exception:
            print(f"Error fetching message {request_id}: {exception}")
        else:
            payload = response["payload"]
            subject = next((h["value"] for h in payload["headers"] if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in payload["headers"] if h["name"] == "From"), "Unknown Sender")
            date_val = next((h["value"] for h in payload["headers"] if h["name"] == "Date"), "No Date")
            snippet = response.get("snippet", "")
            full_text = extract_text_from_payload(payload)
            
            attachments: List[Dict[str, Any]] = []
            if "parts" in payload:
                for part in payload["parts"]:
                    if part.get("filename") and "body" in part:
                        data = part["body"].get("data")
                        if data:
                            attachments.append({
                                "filename": part["filename"],
                                "mimeType": part.get("mimeType", ""),
                                "data": base64.urlsafe_b64decode(data)
                            })

            results.append({
                "from": sender,
                "subject": subject,
                "date": date_val,
                "snippet": snippet,
                "attachments": attachments,
                "full_text": full_text
            })

    # Use the new Gmail batch endpoint
    batch = BatchHttpRequest(callback=callback, batch_uri="https://gmail.googleapis.com/batch/gmail/v1")
    for msg in messages:
        batch.add(service.users().messages().get(userId="me", id=msg["id"], format="full"))

    if messages:
        batch.execute()

    return results