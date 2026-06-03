# ─────────────────────────────────────────────────────────────────────────────
# Pérez Hernández Ricardo — Práctica 8
# Imagen: Servidor de Chat (Flask)
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# wget para healthcheck del docker-compose
RUN apt-get update && apt-get install -y --no-install-recommends wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9000

CMD ["python", "chat_servidor.py"]
