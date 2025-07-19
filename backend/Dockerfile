# backend/Dockerfile

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/backend

# Sistem paketlerini yükle (netcat dahil)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Requirements dosyasını doğru yerden kopyala
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend kodlarını kopyala
COPY backend/ .  

# entrypoint.sh'i doğru yerden kopyala
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# create_superuser.py'yi doğru yerden kopyala  
COPY create_superuser.py /app/backend/create_superuser.py

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8888"]