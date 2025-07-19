# Kişisel Sağlık Takibi

Bu proje, kullanıcıların sağlık verilerini (nabız, tansiyon, oksijen, şeker vb.) ve günlük su/uyku girişlerini takip edebileceği, verileri görselleştiren ve uyarılar sunan bir sistemdir. Proje; Django tabanlı bir web arayüzü, RabbitMQ ile mesajlaşma, InfluxDB ile zaman serisi veri saklama ve Grafana ile görselleştirme içerir.

## Özellikler

- Kullanıcı kaydı ve girişi
- Sağlık sensör verilerinin (nabız, tansiyon, oksijen, şeker) otomatik toplanması
- Günlük su tüketimi ve uyku süresi kaydı
- Anlık uyarılar ve öneriler
- Zaman serisi sağlık verilerinin grafiklerle görselleştirilmesi
- Docker ve docker-compose ile kolay kurulum

## Sistem Mimarisi

- **Producer:** Sensör verilerini simüle ederek RabbitMQ kuyruğuna gönderir.
- **Consumer:** Kuyruktan verileri alır ve InfluxDB'ye kaydeder.
- **Backend (Django):** Kullanıcı arayüzü, kimlik doğrulama, günlük girişler ve grafikler.
- **Veritabanları:** MariaDB (kullanıcı/günlük veriler), InfluxDB (sensör verileri)
- **Grafana:** InfluxDB verilerini gelişmiş şekilde görselleştirmek için kullanılabilir.

## Kurulum

### Gereksinimler

- Docker
- Docker Compose

### Başlatma

1. Ortam değişkenlerini `.env` dosyalarında düzenleyin (gerekirse).
2. Tüm sistemi başlatmak için:
   ```sh
   docker-compose up --build
   ```
3. Uygulama bileşenleri:
   - Django arayüzü: [http://localhost:8888](http://localhost:8888)
   - Adminer (MariaDB yönetimi): [http://localhost:8080](http://localhost:8080)
   - Grafana: [http://localhost:3000](http://localhost:3000)
   - InfluxDB UI: [http://localhost:8086](http://localhost:8086)
   - RabbitMQ yönetimi: [http://localhost:15672](http://localhost:15672) (user/pass: user/pass)

### Kullanıcı Girişi

- İlk açılışta otomatik olarak bir admin kullanıcısı oluşturulur (`admin` / `admin`).
- Kayıt sayfasından yeni kullanıcı oluşturabilirsiniz.

### Sağlık Verileri

- Producer servisi, `producer/kullanicilar.txt` dosyasındaki kullanıcılar için rastgele sağlık verileri üretir.
- Consumer servisi, bu verileri InfluxDB'ye kaydeder.
- Django arayüzünde kendi kullanıcı adınızla giriş yaparak sadece kendi verilerinizi görebilirsiniz.

### Geliştirici Notları

- Kodlar `backend/`, `producer/`, `consumer/` klasörlerinde organize edilmiştir.
- Django ayarları ve ortam değişkenleri için `backend/.env` dosyasını düzenleyin.
- InfluxDB ve RabbitMQ bağlantı ayarları `.env` dosyalarından alınır.

## Lisans

Bu proje [Apache 2.0 Lisansı](LICENSE)