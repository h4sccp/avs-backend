import httpx
from .settings import settings

async def verify_recaptcha(token: str, remote_ip: str) -> bool:
    if not settings.RECAPTCHA_SECRET:
        return True
    if not token:
        return False

    data = {
        "secret": settings.RECAPTCHA_SECRET,
        "response": token,
        "remoteip": remote_ip,
    }
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post("https://www.google.com/recaptcha/api/siteverify", data=data)
            out = r.json()
            return bool(out.get("success"))
    except Exception:
        return False