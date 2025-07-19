# producer/Dockerfile

# Python 3.11 slim imajını kullan
FROM python:3.11-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Python bağımlılıklarını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala (sadece gerekli olanlar)
COPY producer.py .
COPY kullanicilar.txt .

# Uygulamayı çalıştır
CMD ["python", "producer.py"]