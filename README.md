# Class_Clarity

Hello! Welcome to **Class_Clarity**, your personal school email assistant.  
Class_Clarity helps parents organize and visualize events and important dates sent by teachers through email. It automatically fetches emails, extracts key event information, and presents it in a clear, prioritized format — including tables and a calendar view.

---

## How It Works

The following diagram illustrates the flow of data in Class_Clarity:


      +----------------+
      |   Gmail API    |
      | (Teacher Emails)|
      +--------+-------+
               |
               v
      +----------------+
      | fetch_teacher_ |
      | emails()       |
      | (gmail_client) |
      +--------+-------+
               |
               v
      +----------------+
      | parse_email_   |
      | events()       |
      | (llm_parser)   |
      +--------+-------+
               |
               v
      +----------------+
      | FastAPI Backend|
      | (app_backend)  |
      | GET /get_events|
      | Returns JSON   |
      +--------+-------+
               |
               v
      +----------------+
      | Streamlit UI   |
      | (app.py)       |
      | Table + Calendar|
      +--------+-------+
               |
               v
      +----------------+
      | Parent / User  |
      | Views Events   |
      +----------------+

Legend:
- Vertical flow represents data pipeline.
- Backend converts raw emails → structured JSON events.
- Frontend consumes API → visualizes events for the parent.