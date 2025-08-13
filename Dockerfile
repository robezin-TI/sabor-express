FROM python:3.12-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# Criar pastas do app
WORKDIR /app
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código do projeto
COPY src/ ./src/
COPY data/ ./data/
COPY outputs/ ./outputs/

# Expor porta do Streamlit
EXPOSE 8501

# Comando padrão para rodar o app
CMD ["streamlit", "run", "src/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
