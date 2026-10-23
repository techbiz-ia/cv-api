FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY app ./app

# Render usa la variable de entorno PORT. Usamos sh -c para que se evalúe.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]