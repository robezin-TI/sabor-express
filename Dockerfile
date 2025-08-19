FROM python:3.11-slim

# variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# dependências do sistema (necessárias p/ numpy, scikit-learn, requests etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# instalar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copiar todo o código
COPY . .

EXPOSE 5000

# executa o backend servindo também o frontend
CMD ["python", "-m", "src.backend.app"]
