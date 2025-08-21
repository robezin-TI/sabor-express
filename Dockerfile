FROM python:3.10-slim

# instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc g++ make \
    libspatialindex-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copiar arquivos do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# rodar o backend Flask
CMD ["python", "-m", "src.backend.app"]
