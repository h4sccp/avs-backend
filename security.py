import os

def get_secret(name: str, default: str = "") -> str:
    path = f"/run/secrets/{name}"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return os.getenv(name, default)