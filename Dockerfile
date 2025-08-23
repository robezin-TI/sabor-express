FROM python:3.10-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias para OSMnx e GeoPandas
RUN apt-get update && apt-get install -y \
    build-essential \
    libgeos-dev \
    libspatialindex-dev \
    libproj-dev \
    proj-data \
    proj-bin \
    libgdal-dev \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expor porta do Flask
EXPOSE 5000

# Rodar a aplicação
CMD ["python", "app.py"]
