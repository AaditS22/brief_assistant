# Client Briefing Assistant

A small demo tool that takes a client briefing (email/document text) and presents it
in an easier way to a team, providing useful information and analysis.

## Tech stack

- Python + Streamlit for the UI
- Google Gemini API for the AI calls
- Pydantic for structured model output

## Setup

1. Clone the repo and install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add a Gemini API key:

   ```bash
   cp .env.example .env
   ```

3. Run the app:

   ```bash
   streamlit run app.py
   ```
