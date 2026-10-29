# CareerLens AI

A responsive resume analysis platform built with React/Vite/TypeScript and FastAPI.

## Features
- Pasted resume and PDF/DOCX extraction
- Configurable Gemini structured analysis
- Clearly labelled demo fallback without a Gemini key
- Skills, role matches, gap analysis, roadmap, rewrite feedback, JSON/PDF export
- SQLite prototype analysis history

## Start the backend
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
uvicorn app.main:app --app-dir backend --reload --port 8000
```

You can enter the Gemini API key directly in the **Gemini connection** section on the Resume Analyser page. It is sent to the local backend, kept only in that backend process, and cleared when the server restarts.

An optional server environment setup is also supported: copy `.env.example` to `.env` and set `GEMINI_API_KEY`. Without a configured key, the backend uses development demo results and never pretends to call a live AI provider. The model is controlled by `GEMINI_MODEL`.

## Start the frontend
```bash
npm install
npm run dev
```

Vite serves the app at `http://localhost:5173` and proxies `/api` to FastAPI.

## Tests
```bash
pytest -q backend/tests
npm run build
```

## Data and privacy
Uploaded files are parsed in memory and resume text may be saved to local SQLite in prototype history. Delete history entries from the UI/API. Demo mode has no external AI call. When Gemini is enabled, resume text and preferences are sent to Google Gemini according to the selected provider configuration. Use HTTPS and provider retention settings in production.
