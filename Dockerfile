# Dockerfile for GestureBridge AI Backend
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY cert.pem ./cert.pem
COPY key.pem ./key.pem

EXPOSE 5000

CMD ["python", "backend/sign_language_app/live_api.py"]
