FROM python:3.11-slim
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cria pasta media
RUN mkdir -p /app/media

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]EXPOSE 8000
EXPOSE 8000

from app.api.v1 import listings

app.include_router(listings.router, prefix="/api/v1/listings", tags=["listings"])
from pydantic import BaseModel
from typing import Optional