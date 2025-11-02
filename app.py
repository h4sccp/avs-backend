# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
import csv
import uuid
from datetime import datetime

app = FastAPI(title="ATAP Validation Service", version="1.1.0")

# === CORS (add your frontend here if needed) ===
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === CSV directory ===
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# ---------- Helpers ----------
def _csv_path(name: str) -> Path:
    return DATA_DIR / f"{name}.csv"

def _append_csv(path: Path, header: List[str], row: List[str]) -> None:
    """Append a row to CSV; write header if file is new. UTF-8 with BOM for Excel compatibility."""
    is_new = not path.exists()
    with path.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(header)
        writer.writerow(row)

def _read_csv(path: Path) -> List[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)

def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

# ---------- Models ----------
class AppointmentIn(BaseModel):
    name: str
    time: Optional[str] = Field(None, description="ISO datetime, e.g., 2025-11-01T10:00:00")

class EventRegistrationIn(BaseModel):
    name: str
    event: str
    contact: Optional[str] = None

class AssessmentIn(BaseModel):
    patient_id: Optional[str] = None
    score: Optional[float] = None
    notes: Optional[str] = None

# ---------- Root & Status ----------
@app.get("/")
def root():
    return {
        "service": "ATAP Validation Service",
        "storage": "CSV",
        "ok": True,
        "docs": "/docs",
        "browse_data": [
            "/api/appointments (GET)",
            "/api/event_registrations (GET)",
            "/api/assessments (GET)",
            "/api/codes (GET)"
        ],
        "try": ["/status"]
    }

@app.get("/status")
def status():
    return {"status": "ok", "time": _now_iso()}

# ---------- Appointments ----------
@app.post("/api/appointments")
def create_appointment(payload: AppointmentIn):
    rec_id = str(uuid.uuid4())
    path = _csv_path("appointments")
    header = ["id", "name", "time", "created_at"]
    row = [rec_id, payload.name, payload.time or "", _now_iso()]
    _append_csv(path, header, row)
    return {"id": rec_id, "saved": True}

@app.get("/api/appointments")
def list_appointments():
    return _read_csv(_csv_path("appointments"))

# ---------- Code validate / consume (CSV-backed ledger) ----------
# We’ll keep a simple table of codes & states: created/validated/consumed
@app.post("/api/validate/{code}")
def validate_code(code: str):
    path = _csv_path("codes")
    header = ["code", "status", "timestamp"]
    # Append a validate event (you can add logic to check previous state if you like)
    _append_csv(path, header, [code, "validated", _now_iso()])
    return {"code": code, "validated": True}

@app.post("/api/consume/{code}")
def consume_code(code: str):
    path = _csv_path("codes")
    header = ["code", "status", "timestamp"]
    _append_csv(path, header, [code, "consumed", _now_iso()])
    return {"code": code, "consumed": True}

@app.get("/api/codes")
def list_codes():
    return _read_csv(_csv_path("codes"))

# ---------- Event registrations ----------
@app.post("/api/event_registrations")
def register_event(payload: EventRegistrationIn):
    rec_id = str(uuid.uuid4())
    path = _csv_path("event_registrations")
    header = ["id", "name", "event", "contact", "created_at"]
    row = [rec_id, payload.name, payload.event, payload.contact or "", _now_iso()]
    _append_csv(path, header, row)
    return {"id": rec_id, "saved": True}

@app.get("/api/event_registrations")
def list_event_registrations():
    return _read_csv(_csv_path("event_registrations"))

# ---------- Assessments ----------
@app.post("/api/assessments")
def submit_assessment(payload: AssessmentIn):
    rec_id = str(uuid.uuid4())
    path = _csv_path("assessments")
    header = ["id", "patient_id", "score", "notes", "created_at"]
    row = [rec_id, payload.patient_id or "", str(payload.score) if payload.score is not None else "", payload.notes or "", _now_iso()]
    _append_csv(path, header, row)
    return {"id": rec_id, "saved": True}

@app.get("/api/assessments")
def list_assessments():
    return _read_csv(_csv_path("assessments"))

# ---------- Local dev entry ----------
if __name__ == "__main__":
    import uvicorn
    # Bind to 127.0.0.1 for local-only. Use 0.0.0.0 if testing from phone on same Wi-Fi.
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
