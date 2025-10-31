from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ATAP Validation Service")

# CORS setup (allowing local dev and GitHub Pages frontend)
origins = [
    "http://localhost:8080",
    "http://localhost:3000",
    "https://<your-github-username>.github.io"  # replace with your actual site
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/status")
def status():
    return {"status": "ok"}

@app.post("/api/appointments")
def create_appointment():
    # Replace with your logic
    return {"message": "Appointment created"}

@app.post("/api/validate/{code}")
def validate_code(code: str):
    # Replace with your validation logic
    return {"validated": True, "code": code}

@app.post("/api/consume/{code}")
def consume_code(code: str):
    # Replace with your logic
    return {"consumed": True, "code": code}

@app.post("/api/event_registrations")
def register_event():
    # Replace with your logic
    return {"message": "Event registered"}

@app.post("/api/assessments")
def submit_assessment():
    # Replace with your logic
    return {"message": "Assessment submitted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
