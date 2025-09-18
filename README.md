# Class_Clarity

Hello! Welcome to **Class_Clarity**, your personal school email assistant.  
Class_Clarity helps parents organize and visualize events and important dates sent by teachers through email. It automatically fetches emails, extracts key event information, and presents it in a clear, prioritized format — including tables and a calendar view.

---

## How It Works

The following diagram illustrates the flow of data in Class_Clarity:

  +---------------------+
  |      Gmail API      |
  |  (Teacher Emails)   |
  +---------------------+
            |
            v
  +---------------------+
  | fetch_teacher_emails|
  |   (gmail_client)    |
  +---------------------+
            |
            v
  +---------------------+
  |    Data Archiver    |
  |  (archive_manager)  |
  | - Extract email text|
  | - Extract PDF text  |
  | - Merge into LLM-   |
  |   ready format      |
  | - Store locally     |
  +---------------------+
            |
            v
  +---------------------+
  |   LLM Parser /      |
  |     Analyzer        |
  | - Reads preprocessed|
  |   full_text from    |
  |   archive           |
  +---------------------+
            |
            v
  +---------------------+
  |  FastAPI Backend    |
  |   (app_backend)     |
  |   GET /get_events   |
  |   Returns JSON      |
  +---------------------+
            |
            v
  +---------------------+
  |   Streamlit UI      |
  |     (app.py)        |
  |  Table + Calendar   |
  +---------------------+
            |
            v
  +---------------------+
  |   Parent / User     |
  |    Views Events     |
  +---------------------+

Legend:
- Vertical flow represents data pipeline.
- Backend converts raw emails → structured JSON events.
- Frontend consumes API → visualizes events for the parent.



---



## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/shibi-raj/class_clarity.git
cd class_clarity

### 2.  Installation Dependencies
conda env create -f environment.yml
conda activate class_clarity

### 3.  Start backend
uvicorn src.backend.app_backend:app --reload

### 4.  Start frontend
streamlit run src/frontend/app.py

### 5.  Gmail Set Up
1. Place your credentials.json file inside the creds/ folder.

2. Follow the [Google Gmail API Quickstart Guide](https://developers.google.com/workspace/gmail/api/quickstart/python) to generate credentials.

3. Set the list of teacher email addresses in src/backend/gmail_client.py (or your config file).

    Note: Only emails from these addresses will be fetched and parsed into events.  

