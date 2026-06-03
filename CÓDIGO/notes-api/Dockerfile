# ─────────────────────────────────────────────────────────────────────────────
# Pérez Hernández Ricardo — Práctica 8
# Imagen: Microservicio de Notas (FastAPI)
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Instalar wget para el healthcheck del docker-compose
RUN apt-get update && apt-get install -y --no-install-recommends wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
