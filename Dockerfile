FROM python:3.10-slim

WORKDIR /app

# instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copia o código
COPY src ./src

EXPOSE 5000

CMD ["python", "-m", "src.backend.app"]
