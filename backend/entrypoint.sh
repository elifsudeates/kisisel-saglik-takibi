#!/bin/sh
set -e

# PYTHONPATH ayarı
export PYTHONPATH=/app/backend

# MariaDB'nin hazır olmasını bekle
echo "MariaDB'nin hazır olmasını bekleniyor..."
while ! nc -z mariadb 3306; do
  echo "MariaDB henüz hazır değil, 2 saniye bekleniyor..."
  sleep 2
done
echo "MariaDB hazır!"

# InfluxDB'nin hazır olmasını bekle
echo "InfluxDB'nin hazır olmasını bekleniyor..."
while ! nc -z influxdb 8086; do
  echo "InfluxDB henüz hazır değil, 2 saniye bekleniyor..."
  sleep 2
done
echo "InfluxDB hazır!"

# Ek bekleme süresi
echo "Veritabanlarının tamamen başlatılması için 10 saniye bekleniyor..."
sleep 10

# Django projesinin bulunduğu dizine geç
cd /app/backend/backend

echo "Veritabanı geçişleri uygulanıyor..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Süper kullanıcı kontrol ediliyor/oluşturuluyor..."
python /app/backend/create_superuser.py

echo "Sunucu başlatılıyor..."
exec "$@"