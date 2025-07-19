# consumer/Dockerfile

# Python imajını temel al
FROM python:3.12-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Bağımlılıkları kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Uygulamayı çalıştır
CMD ["uvicorn", "consumer:app", "--host", "0.0.0.0", "--port", "8000"]