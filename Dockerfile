FROM python:3.10-slim

# Dependências nativas p/ OSMnx/rtree
RUN apt-get update && apt-get install -y --no-install-recommends \
    libspatialindex-dev libgeos-dev gcc g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Flask expõe 5000
EXPOSE 5000
CMD ["python", "app.py"]
