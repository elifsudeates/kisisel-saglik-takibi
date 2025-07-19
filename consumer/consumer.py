from fastapi import FastAPI
import pika, json, threading, os, time
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv()
app = FastAPI()

# ENV Değişkenleri
rabbit_host = os.getenv("RABBITMQ_HOST")
rabbit_port = int(os.getenv("RABBITMQ_PORT"))
rabbit_user = os.getenv("RABBITMQ_USER")
rabbit_pass = os.getenv("RABBITMQ_PASS")
queue_name = os.getenv("QUEUE_NAME")

influx_url = os.getenv("INFLUXDB_URL")
influx_token = os.getenv("INFLUXDB_TOKEN")
influx_org = os.getenv("INFLUXDB_ORG")
influx_bucket = os.getenv("INFLUXDB_BUCKET")

# Influx bağlantısı
client = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
write_api = client.write_api(write_options=SYNCHRONOUS)

def save_to_influx(data):
    try:
        point = (
            Point("saglik_verisi")
            .tag("user_id", data["user_id"])
            .field("nabiz", data["nabiz"])
            .field("tansiyon_sistolik", data["tansiyon_sistolik"])
            .field("tansiyon_diastolik", data["tansiyon_diastolik"])
            .field("oksijen", data["oksijen"])
            .field("seker", data["seker"])
        )
        write_api.write(bucket=influx_bucket, org=influx_org, record=point)
        print("InfluxDB'ye yazıldı:", data)
    except Exception as e:
        print(f"InfluxDB yazma hatası: {e}")

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        save_to_influx(data)
    except Exception as e:
        print(f"Mesaj işleme hatası: {e}")

def wait_for_rabbitmq():
    """RabbitMQ'nun hazır olmasını bekle"""
    max_retries = 30  # 30 deneme = 5 dakika
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Test bağlantısı
            test_connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=rabbit_host,
                    port=rabbit_port,
                    credentials=pika.PlainCredentials(rabbit_user, rabbit_pass),
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
            time.sleep(10)  # 10 saniye bekle
    
    print("RabbitMQ'ya bağlanılamadı, maksimum deneme sayısına ulaşıldı")
    return False

def consume():
    # RabbitMQ'nun hazır olmasını bekle
    if not wait_for_rabbitmq():
        print("Consumer başlatılamadı: RabbitMQ erişilemez")
        return
    
    while True:
        try:
            print("RabbitMQ'ya bağlanılıyor...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=rabbit_host,
                    port=rabbit_port,
                    credentials=pika.PlainCredentials(rabbit_user, rabbit_pass),
                    connection_attempts=5,
                    retry_delay=5,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )
            channel = connection.channel()
            
            # Queue'yi declare et
            channel.queue_declare(queue=queue_name, durable=True)
            
            # Consumer'ı başlat
            channel.basic_consume(
                queue=queue_name, 
                on_message_callback=callback, 
                auto_ack=True
            )
            
            print(f"Consumer başlatıldı. Queue: {queue_name}")
            channel.start_consuming()
            
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
            try:
                if 'connection' in locals() and not connection.is_closed:
                    connection.close()
            except:
                pass

@app.on_event("startup")
def start_consumer():
    # Consumer'ı daemon thread olarak başlat
    consumer_thread = threading.Thread(target=consume, daemon=True)
    consumer_thread.start()
    print("Consumer thread başlatıldı")

@app.get("/")
def root():
    return {"message": "Consumer aktif", "status": "running"}

@app.get("/health")
def health_check():
    try:
        # InfluxDB bağlantısını test et
        client.ping()
        influx_status = "healthy"
    except:
        influx_status = "unhealthy"
    
    try:
        # RabbitMQ bağlantısını test et
        test_connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=rabbit_host,
                port=rabbit_port,
                credentials=pika.PlainCredentials(rabbit_user, rabbit_pass),
                connection_attempts=1,
                retry_delay=1
            )
        )
        test_connection.close()
        rabbitmq_status = "healthy"
    except:
        rabbitmq_status = "unhealthy"
    
    return {
        "consumer": "running",
        "influxdb": influx_status,
        "rabbitmq": rabbitmq_status
    }