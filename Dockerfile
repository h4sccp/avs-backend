FROM python:3.11-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd -m -u 10001 avs

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY avs/ ./avs/

RUN mkdir -p /data && chown -R avs:avs /data && chown -R avs:avs /app
USER avs

EXPOSE 8080
CMD ["python", "-m", "avs.app"]