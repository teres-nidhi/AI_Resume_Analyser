from __future__ import annotations

import os
import sqlite3
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .ai_service import AIService
from .extractors import extract_resume

DB_PATH = Path(os.getenv("CAREERLENS_DB", "./careerlens.db"))
MAX_TEXT_LENGTH = 100_000
MAX_FILE_SIZE = 5 * 1024 * 1024

app = FastAPI(title="CareerLens AI API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(','), allow_methods=["*"], allow_headers=["*"])

ai = AIService()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS analyses (id TEXT PRIMARY KEY, created_at TEXT DEFAULT CURRENT_TIMESTAMP, resume_text TEXT, result TEXT)")
    conn.commit(); conn.close()

init_db()

class Preferences(BaseModel):
    education_level: Optional[str] = None
    degree: Optional[str] = None
    graduation_year: Optional[int] = Field(None, ge=1980, le=2040)
    industries: list[str] = []
    interests: list[str] = []
    location: Optional[str] = None
    role_type: Optional[str] = None

class AnalyzeRequest(BaseModel):
    resume_text: str = Field(min_length=50, max_length=MAX_TEXT_LENGTH)
    preferences: Preferences = Preferences()

@app.get("/api/health")
def health():
    return {"status": "ok", "demo_mode": ai.demo_mode}

@app.post("/api/analyze")
async def analyze(payload: AnalyzeRequest):
    result = await ai.analyze(payload.resume_text, payload.preferences.model_dump())
    return _save(result, payload.resume_text)

@app.post("/api/analyze/upload")
async def analyze_upload(file: UploadFile = File(...), preferences: str = "{}"):
    if not file.filename:
        raise HTTPException(400, "A resume file is required")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File exceeds the 5 MB limit")
    try:
        text = extract_resume(file.filename, content)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    if len(text.strip()) < 50:
        raise HTTPException(422, "No usable resume text was extracted. Scanned PDFs may require OCR.")
    import json
    try:
        prefs = Preferences.model_validate_json(preferences).model_dump()
    except Exception:
        prefs = {}
    result = await ai.analyze(text, prefs)
    return _save(result, text)

def _save(result, resume_text: str):
    import json
    id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO analyses (id, resume_text, result) VALUES (?, ?, ?)", (id, resume_text[:MAX_TEXT_LENGTH], json.dumps(result.model_dump())))
    conn.commit(); conn.close()
    return {"id": id, **result.model_dump()}

@app.get("/api/analyses")
def list_analyses():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT id, created_at FROM analyses ORDER BY created_at DESC LIMIT 50").fetchall()
    conn.close()
    return [{"id": r[0], "created_at": r[1]} for r in rows]

@app.get("/api/analyses/{id}")
def get_analysis(id: str):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT result FROM analyses WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Analysis not found")
    import json
    return {"id": id, **json.loads(row[0])}

@app.delete("/api/analyses/{id}")
def delete_analysis(id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("DELETE FROM analyses WHERE id = ?", (id,))
    conn.commit(); conn.close()
    if cur.rowcount == 0: raise HTTPException(404, "Analysis not found")
    return {"status": "deleted"}
