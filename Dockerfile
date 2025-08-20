FROM python:3.10-slim

# diretório de trabalho
WORKDIR /app

# instalar dependências do sistema (para compilar libs como osmnx, networkx etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libspatialindex-dev \
    libproj-dev \
    libgeos-dev \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copiar código fonte
COPY src ./src

EXPOSE 5000

# rodar a API
CMD ["python", "-m", "src.backend.app"]
