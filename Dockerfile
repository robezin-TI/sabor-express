FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# dependências do sistema (necessárias p/ numpy, pandas etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copiar todo o projeto
COPY . .

EXPOSE 5000

# comando final - rodar como módulo para evitar erros de import
CMD ["python", "-m", "src.backend.app"]
