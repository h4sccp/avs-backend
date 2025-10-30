from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from datetime import datetime, timedelta, timezone
import uuid

from .settings import settings
from .db import SessionLocal, engine, Base, get_db
from .models import AppointmentRecord, EventRegistration
from .limiter import limiter
from .validators import verify_recaptcha
from .purge import schedule_purge

app = FastAPI(title="ATAP Validation Service (AVS)", version="1.0")

# --- Security Headers / CSP ---
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["Content-Security-Policy"] = settings.CSP
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "interest-cohort=()"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# CORS: lock this to your domain in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Init DB
Base.metadata.create_all(bind=engine)

# Schedule hourly purge of expired/used records
schedule_purge(app)

# --- Health probe ---
@app.get("/status")
async def status():
    return {"ok": True, "utc": datetime.now(timezone.utc).isoformat()}

# --- Appointment booking (anonymous) ---
@app.post("/api/appointments")
@limiter.limit("10/minute")
async def create_appointment(payload: dict, request: Request, db=Depends(get_db)):
    # Optional reCAPTCHA (skipped if secret not set)
    token = payload.get("recaptchaToken")
    if settings.RECAPTCHA_SECRET:
        ok = await verify_recaptcha(token, request.client.host)
        if not ok:
            raise HTTPException(status_code=400, detail="reCAPTCHA failed")

    reason = (payload.get("reason") or "").strip()
    if not reason:
        raise HTTPException(status_code=422, detail="Missing reason")

    # Ephemeral appointment window (15 minutes)
    scheduled_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    expiration_time = scheduled_time + timedelta(minutes=15)

    rec = AppointmentRecord(
        record_id=str(uuid.uuid4()),
        access_code=_access_code(prefix="SCC"),
        scheduled_time=scheduled_time,
        expiration_time=expiration_time,
        service_id="SCRN-HIV",
        is_used=False,
    )
    db.add(rec)
    db.commit()

    return {
        "success": True,
        "appointmentCode": rec.access_code,
        "scheduled_time": rec.scheduled_time.isoformat(),
        "expiration_time": rec.expiration_time.isoformat(),
        "window_minutes": 15,
    }

# --- Validate a code (for staff tablet/scanner) ---
@app.post("/api/validate/{code}")
@limiter.limit("60/minute")
async def validate_code(code: str, db=Depends(get_db)):
    rec = (
        db.query(AppointmentRecord)
        .filter(AppointmentRecord.access_code == code.upper())
        .first()
    )
    if not rec:
        return {"valid": False, "reason": "UNKNOWN_CODE"}

    now = datetime.now(timezone.utc)
    if rec.is_used:
        return {"valid": False, "reason": "ALREADY_USED"}
    if now > rec.expiration_time:
        return {"valid": False, "reason": "EXPIRED"}

    return {
        "valid": True,
        "service_id": rec.service_id,
        "scheduled_time": rec.scheduled_time.isoformat(),
        "expires_in_seconds": int((rec.expiration_time - now).total_seconds()),
    }

# --- Consume a code (mark used) ---
@app.post("/api/consume/{code}")
@limiter.limit("60/minute")
async def consume_code(code: str, db=Depends(get_db)):
    rec = (
        db.query(AppointmentRecord)
        .filter(AppointmentRecord.access_code == code.upper())
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="Not found")
    if rec.is_used:
        return {"success": True, "already": True}

    now = datetime.now(timezone.utc)
    if now > rec.expiration_time:
        raise HTTPException(status_code=410, detail="Expired")

    rec.is_used = True
    db.commit()
    return {"success": True}

# --- Event registrations (store only non-PII + code) ---
@app.post("/api/event_registrations")
@limiter.limit("20/minute")
async def event_register(payload: dict, request: Request, db=Depends(get_db)):
    token = payload.get("recaptchaToken")
    if settings.RECAPTCHA_SECRET:
        ok = await verify_recaptcha(token, request.client.host)
        if not ok:
            raise HTTPException(status_code=400, detail="reCAPTCHA failed")

    event_name = (payload.get("eventName") or "").strip() or "unknown"
    code = _access_code(prefix="EVENT")

    expiry = datetime.now(timezone.utc) + timedelta(days=7)
    rec = EventRegistration(
        record_id=str(uuid.uuid4()),
        access_code=code,
        event_name=event_name,
        expiration_time=expiry,
    )
    db.add(rec)
    db.commit()

    return {"success": True, "registrationCode": code, "expires": expiry.isoformat()}

# --- Assessments (no storage; just a recommendation) ---
@app.post("/api/assessments")
@limiter.limit("30/minute")
async def assessments(payload: dict):
    risk_factors = payload.get("riskFactors") or []
    if not isinstance(risk_factors, list) or len(risk_factors) == 0:
        return {
            "success": True,
            "recommendation": "Please select at least one option to assess your risk.",
            "severity": "info",
        }

    recommendation = (
        "Based on your responses, we recommend booking an appointment for STI/HIV testing. "
        "Our team will provide inclusive, stigma‑free care."
    )
    return {"success": True, "recommendation": recommendation, "severity": "action"}

# --- Error handler for rate limits ---
@app.exception_handler(Exception)
async def on_error(request: Request, exc: Exception):
    if hasattr(exc, "status_code"):
        raise exc
    return JSONResponse(status_code=500, content={"detail": "Server error"})

# --- Helper ---
def _access_code(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[4:8].upper()}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)