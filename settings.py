import os
from pydantic import BaseModel

class _Settings(BaseModel):
    RECAPTCHA_SECRET: str = os.getenv("RECAPTCHA_SECRET", "")
    ALLOW_ORIGINS: list[str] = [
        os.getenv("ALLOW_ORIGIN", "*")
    ]
    CSP: str = (
        "default-src 'self'; "
        "script-src 'self' https://www.google.com https://www.gstatic.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "img-src 'self' data: https://raw.githubusercontent.com https://via.placeholder.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self'; "
        "frame-src https://www.google.com;"
    )

settings = _Settings()