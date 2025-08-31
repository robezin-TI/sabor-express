# Build leve para servir Flask + estáticos
FROM python:3.11-slim

# Dependências do OSMnx
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libspatialindex-dev libgeos-dev libproj-dev proj-bin \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["python", "app.py"]
