# EduTutor AI — Professional Full-Stack Edition

A polished personalized learning assistant built with Streamlit + FastAPI + SQLite, with optional **Groq-powered AI**.

## Security / API key
The Groq API key is **backend-only**.

- Put it in the root `.env` file as `GROQ_API_KEY=...`.
- `frontend/app.py` does not read the key.
- The frontend only calls the local FastAPI backend.
- The key is never rendered in Streamlit and is never sent to the browser.
- Do not commit `.env` to GitHub.

If no valid key is configured, the project automatically falls back to Demo Mode so the assignment can still be demonstrated.

## Run on Windows
1. Extract the ZIP.
2. Open Command Prompt in the project folder.
3. Create the environment file:
   `copy .env.example .env`
4. Open `.env` and add your Groq key. Do **not** put it in frontend code.
5. Install dependencies:
   `pip install -r requirements.txt`
6. Terminal 1:
   `run_backend.bat`
7. Terminal 2:
   `run_frontend.bat`
8. Open the Streamlit URL shown in the terminal.

## Architecture
`Streamlit Frontend → FastAPI Backend → AI Engine / Analytics / Planner → SQLite`

The backend is responsible for authentication, database operations, AI calls, quiz generation, performance analysis, recommendations, and study planning.
