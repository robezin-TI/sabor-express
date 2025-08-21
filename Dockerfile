FROM python:3.10-slim

# libs nativas úteis para OSMnx/rtree
RUN apt-get update && apt-get install -y --no-install-recommends \
    libspatialindex-dev gcc g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# roda como módulo para habilitar imports relativos
CMD ["python", "-m", "src.backend.app"]
