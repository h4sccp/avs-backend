# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

app = FastAPI(title="ATAP Validation Service", version="1.0.0")

# --- CORS ---
# Add your frontend origin(s) here. For GitHub Pages, replace the placeholder.
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:8080",
    "http://localhost:3000",
    "https://<your-github-username>.github.io",  # ← replace with your actual GitHub Pages URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Root route (Option A fix) ---
@app.get("/")
def root():
    return {
        "service": "ATAP Validation Service",
        "ok": True,
        "docs": "/docs",
        "redoc": "/redoc",
        "try": ["/status", "/api/appointments", "/api/validate/{code}", "/api/consume/{code}",
                "/api/event_registrations", "/api/assessments"],
    }

# --- Health/Status ---
@app.get("/status")
def status():
    return {"status": "ok"}

# --- Endpoints (replace stubs with real logic as needed) ---
@app.post("/api/appointments")
def create_appointment():
    # TODO: implement creation logic (e.g., validation, storage)
    return {"message": "Appointment created"}

@app.post("/api/validate/{code}")
def validate_code(code: str):
    # TODO: implement validation logic
    return {"validated": True, "code": code}

@app.post("/api/consume/{code}")
def consume_code(code: str):
    # TODO: implement consume logic (e.g., mark as used)
    return {"consumed": True, "code": code}

@app.post("/api/event_registrations")
def register_event():
    # TODO: implement event registration logic
    return {"message": "Event registered"}

@app.post("/api/assessments")
def submit_assessment():
    # TODO: implement assessment logic
    return {"message": "Assessment submitted"}

# --- Local dev entrypoint ---
if __name__ == "__main__":
    import uvicorn
    # Use port 8080 so the README and Docker mapping are consistent
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
