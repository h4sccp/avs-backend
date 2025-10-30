# ATAP Validation Service (AVS)

Minimal FastAPI backend for zero-budget clinic workflows.

## Run locally
```bash
pip install -r requirements.txt
python -m avs.app
# visit http://localhost:8080/status
```

## Docker
```bash
docker build -t avs .
docker run -p 8080:8080 -v $PWD/data:/data --env-file .env avs
```

## Endpoints
- `GET /status`
- `POST /api/appointments`
- `POST /api/validate/{code}`
- `POST /api/consume/{code}`
- `POST /api/event_registrations`
- `POST /api/assessments`

## Deploy on Render (free)
- Use `render.yaml` (Blueprint). Set `ALLOW_ORIGIN` to your GitHub Pages URL.
- After deploy, your API will be at `https://<your-service>.onrender.com`.
```