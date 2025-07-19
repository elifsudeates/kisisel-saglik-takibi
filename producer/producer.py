import pika
import json
import random
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Ayarları oku
host = os.getenv("RABBITMQ_HOST")
port = int(os.getenv("RABBITMQ_PORT"))
user = os.getenv("RABBITMQ_USER")
passwd = os.getenv("RABBITMQ_PASS")
queue_name = os.getenv("QUEUE_NAME")
kullanici_listesi = os.getenv("KULLANICI_LISTESI")

# Kullanıcıları yükle
with open(kullanici_listesi, 'r') as f:
    kullanicilar = [line.strip() for line in f if line.strip()]

def wait_for_rabbitmq():
    """RabbitMQ'nun hazır olmasını bekle"""
    max_retries = 30  # 5 dakika
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Test bağlantısı
            test_connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=host,
                    port=port,
                    credentials=pika.PlainCredentials(user, passwd),
                    connection_attempts=1,
                    retry_delay=1
                )
            )
            test_connection.close()
            print("RabbitMQ hazır!")
            return True
        except Exception as e:
            retry_count += 1
            print(f"RabbitMQ'ya bağlanılamadı (deneme {retry_count}/{max_retries}): {e}")
            time.sleep(10)
    
    print("RabbitMQ'ya bağlanılamadı, maksimum deneme sayısına ulaşıldı")
    return False

def create_connection():
    """RabbitMQ bağlantısı oluştur"""
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=pika.PlainCredentials(user, passwd),
            connection_attempts=5,
            retry_delay=5,
            heartbeat=600,
            blocked_connection_timeout=300
        )
    )

def generate_data(user_id):
    # %20 ihtimalle anormal veri üret
    anormal = random.random() < 0.2

    if anormal:
        return {
            "user_id": user_id,
            "nabiz": random.choice([random.randint(30, 55), random.randint(110, 180)]),
            "tansiyon_sistolik": random.randint(150, 200),
            "tansiyon_diastolik": random.randint(100, 130),
            "oksijen": round(random.uniform(80, 94), 1),
            "seker": random.choice([random.randint(40, 65), random.randint(160, 250)])
        }
    else:
        return {
            "user_id": user_id,
            "nabiz": random.randint(60, 100),
            "tansiyon_sistolik": random.randint(90, 140),
            "tansiyon_diastolik": random.randint(60, 90),
            "oksijen": round(random.uniform(95, 100), 1),
            "seker": random.randint(70, 140)
        }

# RabbitMQ'nun hazır olmasını bekle
if not wait_for_rabbitmq():
    print("Producer başlatılamadı: RabbitMQ erişilemez")
    exit(1)

# Ana döngü
connection = None
channel = None

while True:
    try:
        # Bağlantı yoksa veya kapalıysa yeniden bağlan
        if not connection or connection.is_closed:
            print("RabbitMQ'ya bağlanılıyor...")
            connection = create_connection()
            channel = connection.channel()
            channel.queue_declare(queue=queue_name, durable=True)
            print("RabbitMQ bağlantısı kuruldu")

        # Her kullanıcı için veri üret ve gönder
        for user_id in kullanicilar:
            try:
                data = generate_data(user_id)
                channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=json.dumps(data),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Mesajı kalıcı yap
                    )
                )
                print(f"Gönderildi: {data}")
            except Exception as e:
                print(f"Mesaj gönderme hatası: {e}")
                # Bağlantıyı kapat ki bir sonraki döngüde yeniden bağlansın
                if connection and not connection.is_closed:
                    connection.close()
                break

        # 30 saniye bekle
        time.sleep(30)

    except pika.exceptions.AMQPConnectionError as e:
        print(f"RabbitMQ bağlantı hatası: {e}")
        print("10 saniye sonra yeniden deneniyor...")
        time.sleep(10)
    except pika.exceptions.StreamLostError as e:
        print(f"RabbitMQ stream hatası: {e}")
        print("5 saniye sonra yeniden deneniyor...")
        time.sleep(5)
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")
        print("15 saniye sonra yeniden deneniyor...")
        time.sleep(15)
    finally:
        # Bağlantıyı güvenli şekilde kapat
        try:
            if connection and not connection.is_closed:
                connection.close()
        except:
            pass