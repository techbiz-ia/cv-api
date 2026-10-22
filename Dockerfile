FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY app ./app

EXPOSE 8000

# Ejecutar como root para evitar conflictos de permisos con volúmenes de Windows
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]